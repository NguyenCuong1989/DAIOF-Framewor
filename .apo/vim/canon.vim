" APΩ VIM CANON — Workspace Editor Control Plane
" VIM_CANON ∈ ℙ_AIOS [EDITOR CONTROL PLANE]
"
" physical_surface = {
"       /Users/andy/.vimrc,
"       ${workspaceRoot}/.apo/vim/canon.vim,
"       vscodevim.vim,
"       AntigravityEditor
"   }
"
" identity:
"   GlobalDispatcher      = /Users/andy/.vimrc
"   WorkspaceCanon        = ${workspaceRoot}/.apo/vim/canon.vim
"   UIAuthoringTarget     = ℒ_UI
"   RuntimeTarget         = A_UI ∪ p₀ ∪ ℬ_BINDING
"
" D_AIOS(𝒱IM_CANON) = {
"       VimEventStream, CanonicalEditorCommand, UIIntent, UIPatch,
"       SourcePatch, ValidationRequest, RenderRequest, HumanEvent
"   }
"
" COMMAND DOMAIN 𝒞_VIM = {
"       APOStage, APOCard, APOBadge, APOChart, APOTable, APOGate,
"       APOBinding, APORender, APOValidate, APOPreview, APOTrace,
"       APOApply, APORollback
"   }
"
" EDITOR EVENT e_vim = (command, buffer, selection, cursor,
"                       workspace, parameters, timestamp)
"
" CanonicalizeVimEvent(e_vim) = UIIntent {
"       intent_id, target_layer, target_component, operation,
"       parameters, source_location, human_authority, policy_snapshot
"   }
"
" AUTHORITY:
"   command_authority = owner
"   mutable_by_extension = false
"   implicit_shell_execution = false
"   source_mutation_requires_APOApply = true
"   preview_before_apply = true
"
" INVARIANT:
"   VimEvent ≠ DirectMutation
"   VimEvent → CanonicalEditorCommand → UIIntent → UIPatch → Validation
"          → Preview → Approval → Render
"
" Chuỗi tác động:
"   Vim key / command → ~/.vimrc → .apo/vim/canon.vim → CanonicalEditorCommand
"   → b_editor → UIIntent → b_ui_authoring → UIPatch → VALID_UI → Preview
"   → APOApply → chat_controller.ts → DOM

" Set leader to Space.  If the host editor (VSCodeVim) does not parse
" 'let mapleader', set 'vim.leader' to " " in editor settings.
let mapleader = " "

" --- UI Authoring commands ---
" Each command emits a CanonicalEditorCommand through ~/.apo/vim/apo_bridge.py,
" which canonicalizes the event and appends it to the local mission-router queue.

" APOStage      → Create(StageViewModel)       → RenderStage
nnoremap <leader>as :!python3 /Users/andy/.apo/vim/apo_bridge.py APOStage<CR>

" APOCard       → Create(CardViewModel)        → Apply(Card)
nnoremap <leader>ac :!python3 /Users/andy/.apo/vim/apo_bridge.py APOCard<CR>

" APOBadge      → Create(ResultViewModel)      → RenderAssertion
nnoremap <leader>ab :!python3 /Users/andy/.apo/vim/apo_bridge.py APOBadge<CR>

" APOChart      → Create(MetricViewModel)      → Apply(Chart)
nnoremap <leader>ach :!python3 /Users/andy/.apo/vim/apo_bridge.py APOChart<CR>

" APOTable      → Create(TableViewModel)       → Apply(TableContainer)
nnoremap <leader>at :!python3 /Users/andy/.apo/vim/apo_bridge.py APOTable<CR>

" APOGate (canon execution) → run apo-canon-gate on workspace state
nnoremap <leader>ag :!cd /Users/andy/tr-gi-p-merge-ready && ./.apo/bin/apo-canon-gate .apo/state/workspace-state.json<CR>

" APOGateComponent → Create(GateViewModel)     → RenderGate
nnoremap <leader>agc :!python3 /Users/andy/.apo/vim/apo_bridge.py APOGate<CR>

" APOBinding    → Create(BindingViewModel)     → ℬ_BINDING
nnoremap <leader>abn :!python3 /Users/andy/.apo/vim/apo_bridge.py APOBinding<CR>

" APORender     → Render_UI
nnoremap <leader>ar :!python3 /Users/andy/.apo/vim/apo_bridge.py APORender<CR>

" APOPreview    → DOM_preview
nnoremap <leader>ap :!python3 /Users/andy/.apo/vim/apo_bridge.py APOPreview<CR>

" APOTrace      → SourceTrace
nnoremap <leader>ax :!python3 /Users/andy/.apo/vim/apo_bridge.py APOTrace<CR>

" APOValidate   → S₂₃ (validation pass)
nnoremap <leader>av :!python3 /Users/andy/.apo/vim/apo_bridge.py APOValidate<CR>

" APOApply      → HumanEvent{type=approve}     → SourcePatch → DOM_(t+1)
nnoremap <leader>aa :!python3 /Users/andy/.apo/vim/apo_bridge.py APOApply<CR>

" APORollback   → HumanEvent{type=redirect}
nnoremap <leader>aro :!python3 /Users/andy/.apo/vim/apo_bridge.py APORollback<CR>
