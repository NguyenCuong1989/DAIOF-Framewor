/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { CancellationToken } from '../../../../base/common/cancellation.js';
import { Disposable } from '../../../../base/common/lifecycle.js';
import { generateUuid } from '../../../../base/common/uuid.js';
import { IConfigurationService } from '../../../../platform/configuration/common/configuration.js';
import { createDecorator } from '../../../../platform/instantiation/common/instantiation.js';
import { ILogService } from '../../../../platform/log/common/log.js';
import { IRequestService, isSuccess } from '../../../../platform/request/common/request.js';
import { IStorageService, StorageScope, StorageTarget } from '../../../../platform/storage/common/storage.js';
import { ChatConfiguration } from './constants.js';

const OUTBOX_STORAGE_KEY = 'chat.executionCanvas.audit.outbox';
const OUTBOX_LIMIT = 512;
const BATCH_LIMIT = 32;

export type ExecutionCanvasStage = 'observe' | 'diagnose' | 'patch' | 'verify' | 'commit';
export type ExecutionCanvasAuditStatus = 'running' | 'passed' | 'failed' | 'canceled';

export interface IExecutionCanvasAuditEvent {
	readonly id: string;
	readonly sessionId: string;
	readonly sequenceNo: number;
	readonly stage: ExecutionCanvasStage;
	readonly eventKind: string;
	readonly status: ExecutionCanvasAuditStatus;
	readonly occurredAt: string;
	readonly payload: Record<string, boolean | number | string | null>;
}

export const IExecutionCanvasAuditService = createDecorator<IExecutionCanvasAuditService>('executionCanvasAuditService');

export interface IExecutionCanvasAuditService {
	readonly _serviceBrand: undefined;
	record(event: Omit<IExecutionCanvasAuditEvent, 'id' | 'sequenceNo' | 'occurredAt'>): void;
	flush(): Promise<void>;
}

export class ExecutionCanvasAuditService extends Disposable implements IExecutionCanvasAuditService {
	declare readonly _serviceBrand: undefined;

	private readonly outbox: IExecutionCanvasAuditEvent[];
	private readonly nextSequence = new Map<string, number>();
	private flushing = false;

	constructor(
		@IConfigurationService private readonly configurationService: IConfigurationService,
		@IStorageService private readonly storageService: IStorageService,
		@IRequestService private readonly requestService: IRequestService,
		@ILogService private readonly logService: ILogService,
	) {
		super();
		this.outbox = this.loadOutbox();
		for (const event of this.outbox) {
			this.nextSequence.set(event.sessionId, Math.max(this.nextSequence.get(event.sessionId) ?? 0, event.sequenceNo + 1));
		}
		if (this.isEnabled()) {
			void this.flush();
		}
	}

	record(event: Omit<IExecutionCanvasAuditEvent, 'id' | 'sequenceNo' | 'occurredAt'>): void {
		if (!this.isEnabled()) {
			return;
		}

		const sequenceNo = this.nextSequence.get(event.sessionId) ?? 0;
		this.nextSequence.set(event.sessionId, sequenceNo + 1);
		this.outbox.push({
			...event,
			id: generateUuid(),
			sequenceNo,
			occurredAt: new Date().toISOString(),
		});
		if (this.outbox.length > OUTBOX_LIMIT) {
			this.outbox.splice(0, this.outbox.length - OUTBOX_LIMIT);
			this.logService.warn('ExecutionCanvasAuditService: outbox limit reached; oldest audit events were dropped');
		}
		this.persist();
		void this.flush();
	}

	async flush(): Promise<void> {
		if (!this.isEnabled() || this.flushing || this.outbox.length === 0) {
			return;
		}

		const endpoint = this.configurationService.getValue<string>(ChatConfiguration.ExecutionCanvasAuditEndpoint);
		if (!endpoint?.startsWith('http://127.0.0.1:') && !endpoint?.startsWith('http://localhost:')) {
			this.logService.warn('ExecutionCanvasAuditService: refusing non-loopback endpoint');
			return;
		}

		this.flushing = true;
		const batch = this.outbox.slice(0, BATCH_LIMIT);
		try {
			const context = await this.requestService.request({
				url: endpoint,
				type: 'POST',
				headers: { 'Content-Type': 'application/json' },
				data: JSON.stringify({ version: 1, events: batch }),
			}, CancellationToken.None);
			if (!isSuccess(context)) {
				this.logService.warn(`ExecutionCanvasAuditService: backend returned ${context.res.statusCode}`);
				return;
			}
			const delivered = new Set(batch.map(event => event.id));
			for (let index = this.outbox.length - 1; index >= 0; index--) {
				if (delivered.has(this.outbox[index].id)) {
					this.outbox.splice(index, 1);
				}
			}
			this.persist();
		} catch (error) {
			this.logService.warn('ExecutionCanvasAuditService: delivery deferred', error);
		} finally {
			this.flushing = false;
		}
	}

	private isEnabled(): boolean {
		return this.configurationService.getValue<boolean>(ChatConfiguration.ExecutionCanvasAuditEnabled) === true;
	}

	private loadOutbox(): IExecutionCanvasAuditEvent[] {
		try {
			const value = JSON.parse(this.storageService.get(OUTBOX_STORAGE_KEY, StorageScope.WORKSPACE, '[]'));
			return Array.isArray(value) ? value.slice(-OUTBOX_LIMIT) : [];
		} catch {
			this.logService.warn('ExecutionCanvasAuditService: invalid persisted outbox was discarded');
			return [];
		}
	}

	private persist(): void {
		this.storageService.store(
			OUTBOX_STORAGE_KEY,
			JSON.stringify(this.outbox),
			StorageScope.WORKSPACE,
			StorageTarget.MACHINE,
		);
	}
}
