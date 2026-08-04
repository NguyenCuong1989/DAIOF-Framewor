#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>
#include <fstream>

namespace apo {

enum class FailureAction {
    None,
    Freeze,
    Reject
};

enum class FailureCode {
    SyntheticNode,
    MissingNode,
    MissingREADME,
    AmbiguousREADME,
    BrokenReference,
    InvariantFailure,
    UnrecordedRuntimeEvent,
    BrokenLineage,
    NonLosslessReconstruction,
    OmegaLocalZero
};

[[nodiscard]] constexpr const char* toString(
    const FailureAction action
) noexcept {
    switch (action) {
        case FailureAction::None:
            return "None";
        case FailureAction::Freeze:
            return "Freeze";
        case FailureAction::Reject:
            return "Reject";
    }

    return "Unknown";
}

[[nodiscard]] constexpr const char* toString(
    const FailureCode code
) noexcept {
    switch (code) {
        case FailureCode::SyntheticNode:
            return "SyntheticNode";
        case FailureCode::MissingNode:
            return "MissingNode";
        case FailureCode::MissingREADME:
            return "MissingREADME";
        case FailureCode::AmbiguousREADME:
            return "AmbiguousREADME";
        case FailureCode::BrokenReference:
            return "BrokenReference";
        case FailureCode::InvariantFailure:
            return "InvariantFailure";
        case FailureCode::UnrecordedRuntimeEvent:
            return "UnrecordedRuntimeEvent";
        case FailureCode::BrokenLineage:
            return "BrokenLineage";
        case FailureCode::NonLosslessReconstruction:
            return "NonLosslessReconstruction";
        case FailureCode::OmegaLocalZero:
            return "OmegaLocalZero";
    }

    return "Unknown";
}

struct ValidationIssue {
    FailureCode code = FailureCode::InvariantFailure;
    FailureAction action = FailureAction::None;
    std::string message;

    bool operator==(const ValidationIssue&) const = default;
};

struct ValidationReport {
    std::vector<ValidationIssue> issues;

    [[nodiscard]] bool valid() const noexcept {
        return issues.empty();
    }

    [[nodiscard]] bool rejected() const noexcept {
        return std::any_of(
            issues.begin(),
            issues.end(),
            [](const ValidationIssue& issue) {
                return issue.action == FailureAction::Reject;
            }
        );
    }

    [[nodiscard]] bool frozen() const noexcept {
        return std::any_of(
            issues.begin(),
            issues.end(),
            [](const ValidationIssue& issue) {
                return issue.action == FailureAction::Freeze;
            }
        );
    }

    [[nodiscard]] FailureAction terminalAction() const noexcept {
        if (rejected()) {
            return FailureAction::Reject;
        }

        if (frozen()) {
            return FailureAction::Freeze;
        }

        return FailureAction::None;
    }

    [[nodiscard]] bool contains(
        const FailureCode code
    ) const noexcept {
        return std::any_of(
            issues.begin(),
            issues.end(),
            [code](const ValidationIssue& issue) {
                return issue.code == code;
            }
        );
    }
};

struct CoreState {
    struct Directory {
        std::string name;
        std::string readmePath;

        bool operator==(const Directory&) const = default;
    };

    struct DirectoryProjection {
        std::string directory;
        std::string readme;

        bool operator==(const DirectoryProjection&) const = default;
    };

    struct GraphNode {
        std::string id;
        std::string label;
        bool synthetic = false;

        bool operator==(const GraphNode&) const = default;
    };

    struct GraphEdge {
        std::string from;
        std::string to;
        std::string label;

        bool operator==(const GraphEdge&) const = default;
    };

    struct Graph {
        std::vector<GraphNode> vertices;
        std::vector<GraphEdge> edges;

        [[nodiscard]] bool nonEmpty() const noexcept {
            return !vertices.empty();
        }

        [[nodiscard]] bool complete() const {
            if (!nonEmpty()) {
                return false;
            }

            std::set<std::string> nodeIds;

            for (const auto& vertex : vertices) {
                if (
                    vertex.id.empty() ||
                    vertex.label.empty()
                ) {
                    return false;
                }

                nodeIds.insert(vertex.id);
            }

            for (const auto& edge : edges) {
                if (
                    edge.from.empty() ||
                    edge.to.empty() ||
                    edge.label.empty() ||
                    !nodeIds.contains(edge.from) ||
                    !nodeIds.contains(edge.to)
                ) {
                    return false;
                }
            }

            return true;
        }

        [[nodiscard]] bool consistent() const {
            std::set<std::string> nodeIds;

            std::set<
                std::tuple<
                    std::string,
                    std::string,
                    std::string
                >
            > edgeKeys;

            for (const auto& vertex : vertices) {
                if (!nodeIds.insert(vertex.id).second) {
                    return false;
                }
            }

            for (const auto& edge : edges) {
                const auto key = std::make_tuple(
                    edge.from,
                    edge.to,
                    edge.label
                );

                if (!edgeKeys.insert(key).second) {
                    return false;
                }
            }

            return true;
        }

        [[nodiscard]] bool deterministic() const {
            std::map<
                std::pair<std::string, std::string>,
                std::string
            > transitions;

            for (const auto& edge : edges) {
                const auto key = std::make_pair(
                    edge.from,
                    edge.label
                );

                const auto [iterator, inserted] =
                    transitions.emplace(key, edge.to);

                if (
                    !inserted &&
                    iterator->second != edge.to
                ) {
                    return false;
                }
            }

            return true;
        }

        [[nodiscard]] bool containsSyntheticNode() const {
            return std::any_of(
                vertices.begin(),
                vertices.end(),
                [](const GraphNode& node) {
                    return node.synthetic;
                }
            );
        }

        [[nodiscard]] bool omegaValue() const {
            return
                complete() &&
                consistent() &&
                nonEmpty();
        }

        [[nodiscard]] bool valid() const {
            return
                omegaValue() &&
                deterministic() &&
                !containsSyntheticNode();
        }

        [[nodiscard]] Graph canonicalized() const {
            Graph result = *this;

            std::sort(
                result.vertices.begin(),
                result.vertices.end(),
                [](const GraphNode& left,
                   const GraphNode& right) {
                    return std::tie(
                               left.id,
                               left.label,
                               left.synthetic
                           ) <
                           std::tie(
                               right.id,
                               right.label,
                               right.synthetic
                           );
                }
            );

            std::sort(
                result.edges.begin(),
                result.edges.end(),
                [](const GraphEdge& left,
                   const GraphEdge& right) {
                    return std::tie(
                               left.from,
                               left.label,
                               left.to
                           ) <
                           std::tie(
                               right.from,
                               right.label,
                               right.to
                           );
                }
            );

            return result;
        }

        bool operator==(const Graph&) const = default;
    };

    struct MultiGraph {
        std::vector<GraphNode> allVertices;
        std::vector<GraphEdge> allEdges;

        bool operator==(const MultiGraph&) const = default;
    };

    struct CanonicalForm {
        std::map<std::string, std::string> invariants;

        bool operator==(const CanonicalForm&) const = default;
    };

    struct GraphSnapshot {
        std::uint64_t revision = 0;
        std::string previousFingerprint;
        std::string fingerprint;
        Graph graph;

        bool operator==(const GraphSnapshot&) const = default;
    };

    struct GraphTimeline {
        std::vector<GraphSnapshot> snapshots;

        [[nodiscard]] bool valid() const;

        [[nodiscard]] const Graph* latest() const noexcept {
            return snapshots.empty()
                ? nullptr
                : &snapshots.back().graph;
        }

        bool operator==(const GraphTimeline&) const = default;
    };

    struct TraceEvent {
        std::string id;
        std::string description;
        std::string sourceDirectory;
        std::uint64_t sequence = 0;

        bool operator==(const TraceEvent&) const = default;
    };

    std::vector<Directory> F;
    std::vector<DirectoryProjection> T;

    std::map<std::string, Graph> G;
    MultiGraph H;

    std::map<std::string, CanonicalForm> Sigma;
    std::map<std::string, GraphTimeline> L;

    std::map<
        std::string,
        std::vector<TraceEvent>
    > tau;

    std::vector<TraceEvent> evidencePlane;
    std::vector<GraphEdge> crossRelations;
};

// JSON deserializers for workspace-state.json
inline void from_json(const nlohmann::json& j, CoreState::Directory& d) {
    j.at("name").get_to(d.name);
    j.at("readmePath").get_to(d.readmePath);
}

inline void from_json(const nlohmann::json& j, CoreState::GraphNode& n) {
    j.at("id").get_to(n.id);
    j.at("label").get_to(n.label);
    n.synthetic = j.value("synthetic", false);
}

inline void from_json(const nlohmann::json& j, CoreState::GraphEdge& e) {
    j.at("from").get_to(e.from);
    j.at("to").get_to(e.to);
    j.at("label").get_to(e.label);
}

inline void from_json(const nlohmann::json& j, CoreState::Graph& g) {
    j.at("vertices").get_to(g.vertices);
    j.at("edges").get_to(g.edges);
}

inline void from_json(const nlohmann::json& j, CoreState::TraceEvent& e) {
    j.at("id").get_to(e.id);
    j.at("description").get_to(e.description);
    j.at("sourceDirectory").get_to(e.sourceDirectory);
    j.at("sequence").get_to(e.sequence);
}

[[nodiscard]] std::uint64_t fnv1a64(
    const std::string& input
) noexcept {
    constexpr std::uint64_t offsetBasis =
        14695981039346656037ULL;

    constexpr std::uint64_t prime =
        1099511628211ULL;

    std::uint64_t hash = offsetBasis;

    for (const unsigned char byte : input) {
        hash ^= byte;
        hash *= prime;
    }

    return hash;
}

[[nodiscard]] std::string graphFingerprint(
    const CoreState::Graph& graph
) {
    const CoreState::Graph canonical =
        graph.canonicalized();

    std::ostringstream payload;

    for (const auto& vertex : canonical.vertices) {
        payload
            << "V:"
            << vertex.id.size()
            << ':'
            << vertex.id
            << ':'
            << vertex.label.size()
            << ':'
            << vertex.label
            << ':'
            << std::boolalpha
            << vertex.synthetic
            << '\n';
    }

    for (const auto& edge : canonical.edges) {
        payload
            << "E:"
            << edge.from.size()
            << ':'
            << edge.from
            << ':'
            << edge.label.size()
            << ':'
            << edge.label
            << ':'
            << edge.to.size()
            << ':'
            << edge.to
            << '\n';
    }

    std::ostringstream result;

    result
        << std::hex
        << std::setw(16)
        << std::setfill('0')
        << fnv1a64(payload.str());

    return result.str();
}

[[nodiscard]] CoreState::CanonicalForm canonicalize(
    const CoreState::Graph& graph
) {
    CoreState::CanonicalForm result;

    result.invariants.emplace(
        "vertexCount",
        std::to_string(graph.vertices.size())
    );

    result.invariants.emplace(
        "edgeCount",
        std::to_string(graph.edges.size())
    );

    result.invariants.emplace(
        "complete",
        graph.complete() ? "true" : "false"
    );

    result.invariants.emplace(
        "consistent",
        graph.consistent() ? "true" : "false"
    );

    result.invariants.emplace(
        "nonEmpty",
        graph.nonEmpty() ? "true" : "false"
    );

    result.invariants.emplace(
        "deterministic",
        graph.deterministic() ? "true" : "false"
    );

    result.invariants.emplace(
        "syntheticFree",
        graph.containsSyntheticNode()
            ? "false"
            : "true"
    );

    result.invariants.emplace(
        "fingerprint",
        graphFingerprint(graph)
    );

    return result;
}

[[nodiscard]] CoreState::GraphSnapshot makeSnapshot(
    const std::uint64_t revision,
    const CoreState::Graph& graph,
    std::string previousFingerprint
) {
    return CoreState::GraphSnapshot{
        revision,
        std::move(previousFingerprint),
        graphFingerprint(graph),
        graph
    };
}

[[nodiscard]] CoreState::GraphTimeline makeTimeline(
    const CoreState::Graph& graph
) {
    CoreState::GraphTimeline timeline;

    timeline.snapshots.push_back(
        makeSnapshot(
            1,
            graph,
            "GENESIS"
        )
    );

    return timeline;
}

bool CoreState::GraphTimeline::valid() const {
    if (snapshots.empty()) {
        return false;
    }

    for (
        std::size_t index = 0;
        index < snapshots.size();
        ++index
    ) {
        const auto& snapshot = snapshots[index];

        if (
            snapshot.revision == 0 ||
            !snapshot.graph.valid() ||
            snapshot.fingerprint !=
                graphFingerprint(snapshot.graph)
        ) {
            return false;
        }

        if (index == 0) {
            if (snapshot.previousFingerprint != "GENESIS") {
                return false;
            }

            continue;
        }

        const auto& previous = snapshots[index - 1];

        if (
            previous.revision >= snapshot.revision ||
            snapshot.previousFingerprint !=
                previous.fingerprint
        ) {
            return false;
        }
    }

    return true;
}

[[nodiscard]] CoreState::MultiGraph buildMultiGraph(
    const std::map<std::string, CoreState::Graph>& graphs,
    const std::vector<CoreState::GraphEdge>& crossRelations
) {
    std::map<std::string, CoreState::GraphNode> vertices;

    std::set<
        std::tuple<
            std::string,
            std::string,
            std::string
        >
    > edges;

    for (const auto& [directory, graph] : graphs) {
        static_cast<void>(directory);

        for (const auto& vertex : graph.vertices) {
            const auto iterator = vertices.find(vertex.id);

            if (iterator == vertices.end()) {
                vertices.emplace(vertex.id, vertex);
                continue;
            }

            if (
                iterator->second.label != vertex.label ||
                iterator->second.synthetic != vertex.synthetic
            ) {
                iterator->second.label.clear();
                iterator->second.synthetic = true;
            }
        }

        for (const auto& edge : graph.edges) {
            edges.emplace(
                edge.from,
                edge.label,
                edge.to
            );
        }
    }

    for (const auto& relation : crossRelations) {
        edges.emplace(
            relation.from,
            relation.label,
            relation.to
        );
    }

    CoreState::MultiGraph result;

    result.allVertices.reserve(vertices.size());
    result.allEdges.reserve(edges.size());

    for (const auto& [id, vertex] : vertices) {
        static_cast<void>(id);
        result.allVertices.push_back(vertex);
    }

    for (const auto& [from, label, to] : edges) {
        result.allEdges.push_back({
            from,
            to,
            label
        });
    }

    return result;
}

[[nodiscard]] bool multiGraphValid(
    const CoreState::MultiGraph& graph
) {
    if (graph.allVertices.empty()) {
        return false;
    }

    std::set<std::string> nodeIds;

    for (const auto& vertex : graph.allVertices) {
        if (
            vertex.id.empty() ||
            vertex.label.empty() ||
            vertex.synthetic ||
            !nodeIds.insert(vertex.id).second
        ) {
            return false;
        }
    }

    std::set<
        std::tuple<
            std::string,
            std::string,
            std::string
        >
    > edgeKeys;

    std::map<
        std::pair<std::string, std::string>,
        std::string
    > transitions;

    for (const auto& edge : graph.allEdges) {
        if (
            edge.from.empty() ||
            edge.to.empty() ||
            edge.label.empty() ||
            !nodeIds.contains(edge.from) ||
            !nodeIds.contains(edge.to)
        ) {
            return false;
        }

        const auto edgeKey = std::make_tuple(
            edge.from,
            edge.label,
            edge.to
        );

        if (!edgeKeys.insert(edgeKey).second) {
            return false;
        }

        const auto transitionKey = std::make_pair(
            edge.from,
            edge.label
        );

        const auto [iterator, inserted] =
            transitions.emplace(
                transitionKey,
                edge.to
            );

        if (
            !inserted &&
            iterator->second != edge.to
        ) {
            return false;
        }
    }

    return true;
}

struct OmegaGate {
    struct OmegaLocal {
        std::string directory;
        bool value = false;

        bool operator==(const OmegaLocal&) const = default;
    };

    enum class Indicator : std::size_t {
        Filesystem = 0,
        UniqueREADME,
        UniqueGraph,
        ProjectionIsomorphic,
        MultiGraph,
        CanonicalAlignment,
        InvariantEvaluation,
        RuntimeTrace,
        EvidencePlane,
        Provenance,
        Lineage,
        LosslessReconstruction,
        Count
    };

    static constexpr std::size_t indicatorCount =
        static_cast<std::size_t>(Indicator::Count);

    static_assert(indicatorCount == 12);

    std::vector<OmegaLocal> omegaList;
    std::array<bool, indicatorCount> indicators{};

    bool omegaGlobal = false;
    int survivalOmega = 0;

    void evaluateGlobal() noexcept {
        survivalOmega = static_cast<int>(
            std::count(
                indicators.begin(),
                indicators.end(),
                true
            )
        );

        const bool allIndicators =
            survivalOmega ==
            static_cast<int>(indicatorCount);

        const bool allLocal =
            !omegaList.empty() &&
            std::all_of(
                omegaList.begin(),
                omegaList.end(),
                [](const OmegaLocal& omega) {
                    return omega.value;
                }
            );

        omegaGlobal =
            allIndicators &&
            allLocal;
    }
};

struct ExecutionOrder {
    enum class Step {
        Filesystem,
        README,
        DirectoryGraph,
        MultiGraph,
        CanonicalForm,
        InvariantEvaluation,
        OmegaEvaluation,
        RuntimeTrace,
        EvidencePlane,
        Lineage,
        Fusion
    };

    inline static constexpr std::array<Step, 11> expected{
        Step::Filesystem,
        Step::README,
        Step::DirectoryGraph,
        Step::MultiGraph,
        Step::CanonicalForm,
        Step::InvariantEvaluation,
        Step::OmegaEvaluation,
        Step::RuntimeTrace,
        Step::EvidencePlane,
        Step::Lineage,
        Step::Fusion
    };

    std::vector<Step> executed;

    void reset() {
        executed.clear();
        executed.reserve(expected.size());
    }

    void mark(const Step step) {
        executed.push_back(step);
    }

    [[nodiscard]] bool complete() const noexcept {
        return
            executed.size() == expected.size() &&
            std::equal(
                executed.begin(),
                executed.end(),
                expected.begin()
            );
    }
};

struct NotebookLMRole {
    const std::string role =
        "ReadOnlySemanticModel";

    const bool inQueue = false;
    const bool inScheduler = false;
    const bool inSecretStore = false;
    const bool inActionAuthority = false;
};

struct DriftControl {
    const bool deterministicGraphRequired = true;
    const bool canonicalAlignmentRequired = true;
    const bool traceableDeltaRequired = true;
    const bool provenanceRequired = true;
    const bool multiPlaneCoherenceRequired = true;
    const bool losslessReconstructionRequired = true;
    const bool immutableHistoryRequired = true;
};

struct FailureDomain {
    const bool syntheticNodeReject = true;
    const bool missingNodeReject = true;
    const bool missingREADMEReject = true;
    const bool ambiguousREADMEFreeze = true;
    const bool brokenReferenceReject = true;
    const bool invariantFailureFreeze = true;
    const bool unrecordedRuntimeEventFreeze = true;
    const bool brokenLineageFreeze = true;
    const bool nonLosslessReconstructionReject = true;
    const bool fusionRejectedIfOmegaZero = true;

    [[nodiscard]] FailureAction actionFor(
        const FailureCode code
    ) const noexcept {
        switch (code) {
            case FailureCode::SyntheticNode:
            case FailureCode::MissingNode:
            case FailureCode::MissingREADME:
            case FailureCode::BrokenReference:
            case FailureCode::NonLosslessReconstruction:
                return FailureAction::Reject;

            case FailureCode::AmbiguousREADME:
            case FailureCode::InvariantFailure:
            case FailureCode::UnrecordedRuntimeEvent:
            case FailureCode::BrokenLineage:
                return FailureAction::Freeze;

            case FailureCode::OmegaLocalZero:
                return FailureAction::None;
        }

        return FailureAction::None;
    }
};

struct CanonicalResult {
    struct DirectoryBinding {
        std::string directory;
        std::string readme;
        CoreState::Graph graph;
        CoreState::CanonicalForm sigma;
        bool omega = false;
        std::vector<CoreState::TraceEvent> tau;
        CoreState::GraphTimeline lineage;

        bool operator==(const DirectoryBinding&) const = default;
    };

    struct FusedOmega {
        bool value = false;
    };

    std::map<std::string, DirectoryBinding> bindings;

    FusedOmega FOmega;
    bool omegaAllOne = false;
    bool fusionRejected = true;

    void evaluateOmega() noexcept {
        omegaAllOne =
            !bindings.empty() &&
            std::all_of(
                bindings.begin(),
                bindings.end(),
                [](const auto& entry) {
                    return entry.second.omega;
                }
            );

        FOmega.value = omegaAllOne;
        fusionRejected = !omegaAllOne;
    }
};

struct SegmentBoundary {
    int major = 0;
    int minor = 0;

    [[nodiscard]] std::string str() const {
        if (minor == 0) {
            return std::to_string(major);
        }

        return
            std::to_string(major) +
            "." +
            std::to_string(minor);
    }

    bool operator==(const SegmentBoundary&) const = default;
};

struct SegmentRange {
    SegmentBoundary start;
    SegmentBoundary end;

    [[nodiscard]] std::string str() const {
        return
            start.str() +
            ".." +
            end.str();
    }

    bool operator==(const SegmentRange&) const = default;
};

inline void from_json(const nlohmann::json& j, SegmentBoundary& sb) {
    const std::string s = j.get<std::string>();
    const auto dot = s.find('.');
    sb.major = std::stoi(s.substr(0, dot));
    sb.minor = (dot == std::string::npos) ? 0 : std::stoi(s.substr(dot + 1));
}

inline void from_json(const nlohmann::json& j, SegmentRange& sr) {
    j.at("start").get_to(sr.start);
    j.at("end").get_to(sr.end);
}


struct Status {
    bool specificationReady = false;

    SegmentBoundary currentBoundary{9, 12};
    SegmentBoundary nextExpectedSegment{9, 13};
    SegmentBoundary continuationTarget{9, 53};
};

class APOLoadState {
public:
    std::string input = "META_SPEC_APO";
    std::string parse = "FAIL";
    std::string type = "APO-Language";

    SegmentRange segmentLoaded{
        SegmentBoundary{1, 0},
        SegmentBoundary{9, 12}
    };

    bool syntheticState = false;
    bool missingState = false;
    bool narrativeInjection = false;

    CoreState coreState;
    OmegaGate omegaGate;
    ExecutionOrder executionOrder;
    NotebookLMRole notebookRole;
    DriftControl driftControl;
    FailureDomain failureDomain;
    CanonicalResult canonicalResult;
    Status status;

    [[nodiscard]] static APOLoadState production();

    [[nodiscard]] ValidationReport selfInitialize() {
        ValidationReport report;

        resetDerivedState();

        parse =
            input == "META_SPEC_APO" &&
            type == "APO-Language"
                ? "PASS"
                : "FAIL";

        stageFilesystem(report);
        stageREADME(report);
        stageDirectoryGraph(report);
        stageMultiGraph(report);
        stageCanonicalForm(report);
        stageInvariantEvaluation(report);
        stageOmegaEvaluation();
        stageRuntimeTrace(report);
        stageEvidencePlane(report);
        stageLineage(report);
        stageFusion(report);

        deriveTopLevelState(report);

        const SegmentRange expectedRange{
            SegmentBoundary{1, 0},
            SegmentBoundary{9, 12}
        };

        status.specificationReady =
            initialized_ &&
            executionOrder.complete() &&
            parse == "PASS" &&
            input == "META_SPEC_APO" &&
            type == "APO-Language" &&
            segmentLoaded == expectedRange &&
            !syntheticState &&
            !missingState &&
            !narrativeInjection &&
            report.valid() &&
            omegaGate.survivalOmega == 12 &&
            omegaGate.omegaGlobal &&
            canonicalResult.omegaAllOne &&
            canonicalResult.FOmega.value &&
            !canonicalResult.fusionRejected;

        return report;
    }

    [[nodiscard]] bool initialized() const noexcept {
        return initialized_;
    }

    [[nodiscard]] static APOLoadState fromWorkspaceManifest(
        const std::string& manifestPath
    );

private:
    bool initialized_ = false;

    void resetDerivedState() {
        initialized_ = false;

        coreState.T.clear();
        coreState.H = {};
        coreState.Sigma.clear();
        coreState.evidencePlane.clear();

        omegaGate.omegaList.clear();
        omegaGate.indicators.fill(false);
        omegaGate.omegaGlobal = false;
        omegaGate.survivalOmega = 0;

        canonicalResult.bindings.clear();
        canonicalResult.omegaAllOne = false;
        canonicalResult.FOmega.value = false;
        canonicalResult.fusionRejected = true;

        executionOrder.reset();

        syntheticState = false;
        missingState = false;
        status.specificationReady = false;
    }

    void addIssue(
        ValidationReport& report,
        const FailureCode code,
        std::string message
    ) const {
        const ValidationIssue issue{
            code,
            failureDomain.actionFor(code),
            std::move(message)
        };

        if (
            std::find(
                report.issues.begin(),
                report.issues.end(),
                issue
            ) == report.issues.end()
        ) {
            report.issues.push_back(issue);
        }
    }

    void setIndicator(
        const OmegaGate::Indicator indicator,
        const bool value
    ) noexcept {
        omegaGate.indicators[
            static_cast<std::size_t>(indicator)
        ] = value;
    }

    [[nodiscard]] std::set<std::string>
    directoryNames() const {
        std::set<std::string> result;

        for (const auto& directory : coreState.F) {
            result.insert(directory.name);
        }

        return result;
    }

    void stageFilesystem(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::Filesystem
        );

        bool valid = !coreState.F.empty();
        std::set<std::string> names;

        for (const auto& directory : coreState.F) {
            if (
                directory.name.empty() ||
                !names.insert(directory.name).second
            ) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::MissingNode,
                    "DirectorySet contains an empty or duplicate directory."
                );
            }
        }

        setIndicator(
            OmegaGate::Indicator::Filesystem,
            valid
        );
    }

    void stageREADME(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::README
        );

        bool uniqueReadmes = !coreState.F.empty();
        std::set<std::string> readmes;

        coreState.T.clear();
        coreState.T.reserve(coreState.F.size());

        for (const auto& directory : coreState.F) {
            if (directory.readmePath.empty()) {
                uniqueReadmes = false;

                addIssue(
                    report,
                    FailureCode::MissingREADME,
                    "Directory '" +
                        directory.name +
                        "' has no README."
                );
            } else if (
                !readmes.insert(
                    directory.readmePath
                ).second
            ) {
                uniqueReadmes = false;

                addIssue(
                    report,
                    FailureCode::AmbiguousREADME,
                    "README '" +
                        directory.readmePath +
                        "' is bound to multiple directories."
                );
            }

            coreState.T.push_back({
                directory.name,
                directory.readmePath
            });
        }

        std::sort(
            coreState.T.begin(),
            coreState.T.end(),
            [](const CoreState::DirectoryProjection& left,
               const CoreState::DirectoryProjection& right) {
                return std::tie(
                           left.directory,
                           left.readme
                       ) <
                       std::tie(
                           right.directory,
                           right.readme
                       );
            }
        );

        std::set<
            std::pair<std::string, std::string>
        > sourceProjection;

        std::set<
            std::pair<std::string, std::string>
        > derivedProjection;

        for (const auto& directory : coreState.F) {
            sourceProjection.emplace(
                directory.name,
                directory.readmePath
            );
        }

        for (const auto& projection : coreState.T) {
            derivedProjection.emplace(
                projection.directory,
                projection.readme
            );
        }

        const bool isomorphic =
            !sourceProjection.empty() &&
            sourceProjection == derivedProjection &&
            sourceProjection.size() == coreState.F.size() &&
            derivedProjection.size() == coreState.T.size();

        setIndicator(
            OmegaGate::Indicator::UniqueREADME,
            uniqueReadmes
        );

        setIndicator(
            OmegaGate::Indicator::ProjectionIsomorphic,
            isomorphic
        );

        if (!isomorphic) {
            addIssue(
                report,
                FailureCode::InvariantFailure,
                "Projection T is not isomorphic to DirectorySet F."
            );
        }
    }

    void stageDirectoryGraph(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::DirectoryGraph
        );

        const std::set<std::string> expected =
            directoryNames();

        std::set<std::string> actual;

        for (const auto& [directory, graph] : coreState.G) {
            static_cast<void>(graph);
            actual.insert(directory);
        }

        bool valid =
            !expected.empty() &&
            expected == actual;

        for (const auto& directory : expected) {
            if (!coreState.G.contains(directory)) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::MissingNode,
                    "Directory '" +
                        directory +
                        "' has no unique graph."
                );
            }
        }

        for (const auto& directory : actual) {
            if (!expected.contains(directory)) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::SyntheticNode,
                    "Graph for undeclared directory '" +
                        directory +
                        "' is synthetic."
                );
            }
        }

        for (const auto& [directory, graph] : coreState.G) {
            if (graph.containsSyntheticNode()) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::SyntheticNode,
                    "Graph '" +
                        directory +
                        "' contains a synthetic node."
                );
            }
        }

        setIndicator(
            OmegaGate::Indicator::UniqueGraph,
            valid
        );
    }

    void stageMultiGraph(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::MultiGraph
        );

        coreState.H = buildMultiGraph(
            coreState.G,
            coreState.crossRelations
        );

        const CoreState::MultiGraph reconstructed =
            buildMultiGraph(
                coreState.G,
                coreState.crossRelations
            );

        const bool valid =
            coreState.H == reconstructed &&
            multiGraphValid(coreState.H);

        setIndicator(
            OmegaGate::Indicator::MultiGraph,
            valid
        );

        if (!valid) {
            addIssue(
                report,
                FailureCode::BrokenReference,
                "MultiGraph contains conflicts, non-determinism, or broken references."
            );
        }
    }

    void stageCanonicalForm(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::CanonicalForm
        );

        coreState.Sigma.clear();

        for (const auto& [directory, graph] : coreState.G) {
            coreState.Sigma.emplace(
                directory,
                canonicalize(graph)
            );
        }

        bool valid =
            coreState.Sigma.size() ==
            coreState.G.size();

        for (const auto& [directory, graph] : coreState.G) {
            const auto iterator =
                coreState.Sigma.find(directory);

            if (
                iterator == coreState.Sigma.end() ||
                iterator->second != canonicalize(graph)
            ) {
                valid = false;
                break;
            }
        }

        setIndicator(
            OmegaGate::Indicator::CanonicalAlignment,
            valid
        );

        if (!valid) {
            addIssue(
                report,
                FailureCode::InvariantFailure,
                "Canonical forms are not aligned with source graphs."
            );
        }
    }

    void stageInvariantEvaluation(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::InvariantEvaluation
        );

        bool valid = !coreState.G.empty();

        for (const auto& [directory, graph] : coreState.G) {
            if (!graph.omegaValue()) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::InvariantFailure,
                    "Graph '" +
                        directory +
                        "' is incomplete, inconsistent, or empty."
                );
            }

            if (!graph.deterministic()) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::InvariantFailure,
                    "Graph '" +
                        directory +
                        "' is non-deterministic."
                );
            }

            if (graph.containsSyntheticNode()) {
                valid = false;

                addIssue(
                    report,
                    FailureCode::SyntheticNode,
                    "Graph '" +
                        directory +
                        "' contains synthetic state."
                );
            }
        }

        setIndicator(
            OmegaGate::Indicator::InvariantEvaluation,
            valid
        );
    }

    void stageOmegaEvaluation() {
        executionOrder.mark(
            ExecutionOrder::Step::OmegaEvaluation
        );

        omegaGate.omegaList.clear();
        omegaGate.omegaList.reserve(coreState.F.size());

        for (const auto& directory : coreState.F) {
            const auto graphIterator =
                coreState.G.find(directory.name);

            const bool value =
                graphIterator != coreState.G.end() &&
                graphIterator->second.omegaValue();

            omegaGate.omegaList.push_back({
                directory.name,
                value
            });
        }
    }

    void stageRuntimeTrace(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::RuntimeTrace
        );

        const std::set<std::string> expected =
            directoryNames();

        std::set<std::string> actual;
        std::set<std::string> eventIds;
        std::set<std::uint64_t> sequences;

        bool traceValid =
            !coreState.tau.empty();

        bool provenanceValid =
            !coreState.tau.empty();

        for (const auto& [directory, trace] : coreState.tau) {
            actual.insert(directory);

            if (trace.empty()) {
                traceValid = false;
            }

            if (!expected.contains(directory)) {
                provenanceValid = false;
            }

            for (const auto& event : trace) {
                if (
                    event.id.empty() ||
                    event.description.empty() ||
                    event.sourceDirectory.empty() ||
                    event.sequence == 0 ||
                    !eventIds.insert(event.id).second ||
                    !sequences.insert(event.sequence).second
                ) {
                    traceValid = false;
                }

                if (
                    event.sourceDirectory != directory ||
                    !expected.contains(
                        event.sourceDirectory
                    )
                ) {
                    provenanceValid = false;
                }
            }
        }

        traceValid =
            traceValid &&
            actual == expected;

        provenanceValid =
            provenanceValid &&
            actual == expected;

        setIndicator(
            OmegaGate::Indicator::RuntimeTrace,
            traceValid
        );

        setIndicator(
            OmegaGate::Indicator::Provenance,
            provenanceValid
        );

        if (!traceValid) {
            addIssue(
                report,
                FailureCode::UnrecordedRuntimeEvent,
                "Runtime traces are missing, duplicated, or malformed."
            );
        }

        if (!provenanceValid) {
            addIssue(
                report,
                FailureCode::InvariantFailure,
                "Runtime trace provenance is detached from directory identity."
            );
        }
    }

    void stageEvidencePlane(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::EvidencePlane
        );

        coreState.evidencePlane.clear();

        std::size_t expectedEventCount = 0;

        for (const auto& [directory, trace] : coreState.tau) {
            static_cast<void>(directory);

            expectedEventCount += trace.size();

            coreState.evidencePlane.insert(
                coreState.evidencePlane.end(),
                trace.begin(),
                trace.end()
            );
        }

        std::sort(
            coreState.evidencePlane.begin(),
            coreState.evidencePlane.end(),
            [](const CoreState::TraceEvent& left,
               const CoreState::TraceEvent& right) {
                return std::tie(
                           left.sequence,
                           left.id
                       ) <
                       std::tie(
                           right.sequence,
                           right.id
                       );
            }
        );

        std::vector<CoreState::TraceEvent> reconstructed;

        for (const auto& [directory, trace] : coreState.tau) {
            static_cast<void>(directory);

            reconstructed.insert(
                reconstructed.end(),
                trace.begin(),
                trace.end()
            );
        }

        std::sort(
            reconstructed.begin(),
            reconstructed.end(),
            [](const CoreState::TraceEvent& left,
               const CoreState::TraceEvent& right) {
                return std::tie(
                           left.sequence,
                           left.id
                       ) <
                       std::tie(
                           right.sequence,
                           right.id
                       );
            }
        );

        const bool valid =
            expectedEventCount > 0 &&
            coreState.evidencePlane.size() ==
                expectedEventCount &&
            coreState.evidencePlane == reconstructed;

        setIndicator(
            OmegaGate::Indicator::EvidencePlane,
            valid
        );

        if (!valid) {
            addIssue(
                report,
                FailureCode::UnrecordedRuntimeEvent,
                "EvidencePlane is not the complete union of runtime traces."
            );
        }
    }

    void stageLineage(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::Lineage
        );

        const std::set<std::string> expected =
            directoryNames();

        std::set<std::string> actual;
        bool valid = !coreState.L.empty();

        for (const auto& [directory, timeline] : coreState.L) {
            actual.insert(directory);

            const auto graphIterator =
                coreState.G.find(directory);

            const CoreState::Graph* latest =
                timeline.latest();

            if (
                graphIterator == coreState.G.end() ||
                !timeline.valid() ||
                latest == nullptr ||
                latest->canonicalized() !=
                    graphIterator->second.canonicalized()
            ) {
                valid = false;
            }
        }

        valid =
            valid &&
            expected == actual;

        setIndicator(
            OmegaGate::Indicator::Lineage,
            valid
        );

        if (!valid) {
            addIssue(
                report,
                FailureCode::BrokenLineage,
                "Graph lineage is missing, mutable, or detached from current state."
            );
        }
    }

    void stageFusion(
        ValidationReport& report
    ) {
        executionOrder.mark(
            ExecutionOrder::Step::Fusion
        );

        canonicalResult.bindings.clear();

        for (const auto& directory : coreState.F) {
            const auto graphIterator =
                coreState.G.find(directory.name);

            const auto sigmaIterator =
                coreState.Sigma.find(directory.name);

            const auto traceIterator =
                coreState.tau.find(directory.name);

            const auto lineageIterator =
                coreState.L.find(directory.name);

            if (
                graphIterator == coreState.G.end() ||
                sigmaIterator == coreState.Sigma.end() ||
                traceIterator == coreState.tau.end() ||
                lineageIterator == coreState.L.end()
            ) {
                continue;
            }

            canonicalResult.bindings.emplace(
                directory.name,
                CanonicalResult::DirectoryBinding{
                    directory.name,
                    directory.readmePath,
                    graphIterator->second,
                    sigmaIterator->second,
                    graphIterator->second.omegaValue(),
                    traceIterator->second,
                    lineageIterator->second
                }
            );
        }

        std::map<std::string, std::string>
            expectedReadmes;

        for (const auto& directory : coreState.F) {
            expectedReadmes.emplace(
                directory.name,
                directory.readmePath
            );
        }

        std::map<std::string, std::string>
            reconstructedReadmes;

        std::map<std::string, CoreState::Graph>
            reconstructedGraphs;

        std::map<
            std::string,
            CoreState::CanonicalForm
        > reconstructedSigma;

        std::map<
            std::string,
            CoreState::GraphTimeline
        > reconstructedLineage;

        std::map<
            std::string,
            std::vector<CoreState::TraceEvent>
        > reconstructedTraces;

        std::vector<CoreState::TraceEvent>
            reconstructedEvidence;

        bool bindingIdentityValid = true;

        for (
            const auto& [directory, binding] :
            canonicalResult.bindings
        ) {
            if (
                binding.directory != directory ||
                binding.omega !=
                    binding.graph.omegaValue()
            ) {
                bindingIdentityValid = false;
            }

            reconstructedReadmes.emplace(
                directory,
                binding.readme
            );

            reconstructedGraphs.emplace(
                directory,
                binding.graph
            );

            reconstructedSigma.emplace(
                directory,
                binding.sigma
            );

            reconstructedLineage.emplace(
                directory,
                binding.lineage
            );

            reconstructedTraces.emplace(
                directory,
                binding.tau
            );

            reconstructedEvidence.insert(
                reconstructedEvidence.end(),
                binding.tau.begin(),
                binding.tau.end()
            );
        }

        std::sort(
            reconstructedEvidence.begin(),
            reconstructedEvidence.end(),
            [](const CoreState::TraceEvent& left,
               const CoreState::TraceEvent& right) {
                return std::tie(
                           left.sequence,
                           left.id
                       ) <
                       std::tie(
                           right.sequence,
                           right.id
                       );
            }
        );

        const CoreState::MultiGraph
            reconstructedMultiGraph =
                buildMultiGraph(
                    reconstructedGraphs,
                    coreState.crossRelations
                );

        const bool lossless =
            bindingIdentityValid &&
            !canonicalResult.bindings.empty() &&
            canonicalResult.bindings.size() ==
                coreState.F.size() &&
            reconstructedReadmes ==
                expectedReadmes &&
            reconstructedGraphs ==
                coreState.G &&
            reconstructedSigma ==
                coreState.Sigma &&
            reconstructedLineage ==
                coreState.L &&
            reconstructedTraces ==
                coreState.tau &&
            reconstructedEvidence ==
                coreState.evidencePlane &&
            reconstructedMultiGraph ==
                coreState.H;

        setIndicator(
            OmegaGate::Indicator::LosslessReconstruction,
            lossless
        );

        if (!lossless) {
            addIssue(
                report,
                FailureCode::NonLosslessReconstruction,
                "Canonical bindings cannot reconstruct source state losslessly."
            );
        }

        if (!executionOrder.complete()) {
            setIndicator(
                OmegaGate::Indicator::InvariantEvaluation,
                false
            );

            addIssue(
                report,
                FailureCode::InvariantFailure,
                "Execution order does not match the canonical pipeline."
            );
        }

        for (const auto& omega : omegaGate.omegaList) {
            if (!omega.value) {
                addIssue(
                    report,
                    FailureCode::OmegaLocalZero,
                    "Local omega for directory '" +
                        omega.directory +
                        "' is zero."
                );
            }
        }

        omegaGate.evaluateGlobal();
        canonicalResult.evaluateOmega();

        if (!omegaGate.omegaGlobal) {
            canonicalResult.omegaAllOne = false;
            canonicalResult.FOmega.value = false;
            canonicalResult.fusionRejected = true;
        }

        initialized_ = true;
    }

    void deriveTopLevelState(
        const ValidationReport& report
    ) {
        syntheticState =
            report.contains(
                FailureCode::SyntheticNode
            );

        missingState =
            report.contains(
                FailureCode::MissingNode
            ) ||
            report.contains(
                FailureCode::MissingREADME
            ) ||
            report.contains(
                FailureCode::UnrecordedRuntimeEvent
            ) ||
            report.contains(
                FailureCode::BrokenLineage
            );
    }
};

[[nodiscard]] CoreState::Graph makeCoreGraph() {
    return CoreState::Graph{
        {
            {
                "meta_spec_apo",
                "META_SPEC_APO",
                false
            },
            {
                "directory_set",
                "DirectorySet",
                false
            },
            {
                "directory_projection",
                "DirectoryProjection",
                false
            },
            {
                "directory_graph",
                "DirectoryGraph",
                false
            },
            {
                "omega_gate",
                "OmegaGate",
                false
            }
        },
        {
            {
                "meta_spec_apo",
                "directory_set",
                "defines_directory_set"
            },
            {
                "directory_set",
                "directory_projection",
                "projects_directory_set"
            },
            {
                "directory_projection",
                "directory_graph",
                "binds_directory_graph"
            },
            {
                "directory_graph",
                "omega_gate",
                "feeds_omega_gate"
            }
        }
    };
}

[[nodiscard]] CoreState::Graph makeRuntimeGraph() {
    return CoreState::Graph{
        {
            {
                "runtime_trace",
                "RuntimeTrace",
                false
            },
            {
                "evidence_plane",
                "EvidencePlane",
                false
            },
            {
                "lineage",
                "Lineage",
                false
            },
            {
                "fusion",
                "Fusion",
                false
            }
        },
        {
            {
                "runtime_trace",
                "evidence_plane",
                "projects_evidence"
            },
            {
                "evidence_plane",
                "lineage",
                "supports_lineage"
            },
            {
                "lineage",
                "fusion",
                "authorizes_fusion"
            }
        }
    };
}

[[nodiscard]] CoreState::Graph makePolicyGraph() {
    return CoreState::Graph{
        {
            {
                "drift_control",
                "DriftControl",
                false
            },
            {
                "failure_domain",
                "FailureDomain",
                false
            },
            {
                "notebooklm_role",
                "ReadOnlySemanticModel",
                false
            },
            {
                "canonical_result",
                "CanonicalResult",
                false
            }
        },
        {
            {
                "drift_control",
                "failure_domain",
                "constrains_failure_domain"
            },
            {
                "notebooklm_role",
                "canonical_result",
                "observes_canonical_result"
            },
            {
                "failure_domain",
                "canonical_result",
                "guards_canonical_result"
            }
        }
    };
}

APOLoadState APOLoadState::production() {
    APOLoadState state;

    const CoreState::Graph coreGraph =
        makeCoreGraph();

    const CoreState::Graph runtimeGraph =
        makeRuntimeGraph();

    const CoreState::Graph policyGraph =
        makePolicyGraph();

    state.coreState.F = {
        {
            "core",
            "/apo/core/README.md"
        },
        {
            "runtime",
            "/apo/runtime/README.md"
        },
        {
            "policy",
            "/apo/policy/README.md"
        }
    };

    state.coreState.G = {
        {
            "core",
            coreGraph
        },
        {
            "runtime",
            runtimeGraph
        },
        {
            "policy",
            policyGraph
        }
    };

    state.coreState.crossRelations = {
        {
            "omega_gate",
            "runtime_trace",
            "permits_runtime_trace"
        },
        {
            "drift_control",
            "omega_gate",
            "constrains_omega_gate"
        },
        {
            "failure_domain",
            "fusion",
            "guards_fusion"
        },
        {
            "evidence_plane",
            "canonical_result",
            "supports_canonical_result"
        }
    };

    state.coreState.L = {
        {
            "core",
            makeTimeline(coreGraph)
        },
        {
            "runtime",
            makeTimeline(runtimeGraph)
        },
        {
            "policy",
            makeTimeline(policyGraph)
        }
    };

    state.coreState.tau = {
        {
            "core",
            {
                {
                    "evt-core-001",
                    "Core README parsed into a deterministic directory graph.",
                    "core",
                    1
                },
                {
                    "evt-core-002",
                    "Directory projection derived from DirectorySet.",
                    "core",
                    2
                },
                {
                    "evt-core-003",
                    "Core graph canonical invariants evaluated.",
                    "core",
                    3
                }
            }
        },
        {
            "runtime",
            {
                {
                    "evt-runtime-001",
                    "Runtime events recorded into an ordered trace.",
                    "runtime",
                    4
                },
                {
                    "evt-runtime-002",
                    "Runtime trace projected into EvidencePlane.",
                    "runtime",
                    5
                },
                {
                    "evt-runtime-003",
                    "Runtime lineage bound to the current graph state.",
                    "runtime",
                    6
                }
            }
        },
        {
            "policy",
            {
                {
                    "evt-policy-001",
                    "Drift-control invariants loaded as required policy.",
                    "policy",
                    7
                },
                {
                    "evt-policy-002",
                    "Failure-domain actions bound to validation codes.",
                    "policy",
                    8
                },
                {
                    "evt-policy-003",
                    "Read-only semantic role verified without action authority.",
                    "policy",
                    9
                }
            }
        }
    };

    return state;
}


APOLoadState APOLoadState::fromWorkspaceManifest(
    const std::string& manifestPath
) {
    std::ifstream file(manifestPath);
    if (!file) {
        throw std::runtime_error("Cannot open workspace manifest: " + manifestPath);
    }

    nlohmann::json j;
    file >> j;

    APOLoadState state;

    state.input = j.value("input", "META_SPEC_APO");
    state.type = j.value("type", "APO-Language");

    if (j.contains("segmentLoaded")) {
        j.at("segmentLoaded").get_to(state.segmentLoaded);
    }

    for (const auto& dir : j.at("directories")) {
        CoreState::Directory d;
        dir.get_to(d);
        state.coreState.F.push_back(std::move(d));
    }

    for (const auto& [key, value] : j.at("graphs").items()) {
        CoreState::Graph g;
        value.get_to(g);
        state.coreState.G.emplace(key, std::move(g));
    }

    for (const auto& rel : j.at("crossRelations")) {
        CoreState::GraphEdge e;
        rel.get_to(e);
        state.coreState.crossRelations.push_back(std::move(e));
    }

    for (const auto& [key, trace] : j.at("runtimeTraces").items()) {
        std::vector<CoreState::TraceEvent> events;
        for (const auto& ev : trace) {
            CoreState::TraceEvent e;
            ev.get_to(e);
            events.push_back(std::move(e));
        }
        state.coreState.tau.emplace(key, std::move(events));
    }

    // Build lineage from source graphs so fingerprints are always consistent.
    for (const auto& [dir, graph] : state.coreState.G) {
        state.coreState.L.emplace(dir, makeTimeline(graph));
    }

    return state;
}


void printState(
    const APOLoadState& state,
    const ValidationReport& report
) {
    std::cout
        << std::boolalpha
        << "APO_LOAD_STATE\n"
        << "{\n"
        << "  Input=" << state.input << '\n'
        << "  Parse=" << state.parse << '\n'
        << "  Type=" << state.type << '\n'
        << "  SegmentLoaded="
        << state.segmentLoaded.str() << '\n'
        << "  SyntheticState="
        << state.syntheticState << '\n'
        << "  MissingState="
        << state.missingState << '\n'
        << "  NarrativeInjection="
        << state.narrativeInjection << '\n'
        << "  Initialized="
        << state.initialized() << '\n'
        << "  ExecutionOrderValid="
        << state.executionOrder.complete() << '\n'
        << '\n'
        << "  DirectoryCount="
        << state.coreState.F.size() << '\n'
        << "  ProjectionCount="
        << state.coreState.T.size() << '\n'
        << "  GraphCount="
        << state.coreState.G.size() << '\n'
        << "  MultiGraphVertexCount="
        << state.coreState.H.allVertices.size() << '\n'
        << "  MultiGraphEdgeCount="
        << state.coreState.H.allEdges.size() << '\n'
        << "  CanonicalFormCount="
        << state.coreState.Sigma.size() << '\n'
        << "  TracePlaneCount="
        << state.coreState.tau.size() << '\n'
        << "  EvidenceEventCount="
        << state.coreState.evidencePlane.size() << '\n'
        << "  LineageCount="
        << state.coreState.L.size() << '\n'
        << "  BindingCount="
        << state.canonicalResult.bindings.size() << '\n'
        << '\n'
        << "  SurvivalOmega="
        << state.omegaGate.survivalOmega << '\n'
        << "  OmegaGlobal="
        << state.omegaGate.omegaGlobal << '\n'
        << "  OmegaAllOne="
        << state.canonicalResult.omegaAllOne << '\n'
        << "  FusedOmega="
        << state.canonicalResult.FOmega.value << '\n'
        << "  FusionRejected="
        << state.canonicalResult.fusionRejected << '\n'
        << '\n'
        << "  ValidationIssueCount="
        << report.issues.size() << '\n'
        << "  ValidationValid="
        << report.valid() << '\n'
        << "  FailureAction="
        << toString(report.terminalAction()) << '\n'
        << '\n'
        << "  NotebookLMRole="
        << state.notebookRole.role << '\n'
        << "  NotebookLMInQueue="
        << state.notebookRole.inQueue << '\n'
        << "  NotebookLMInScheduler="
        << state.notebookRole.inScheduler << '\n'
        << "  NotebookLMInSecretStore="
        << state.notebookRole.inSecretStore << '\n'
        << "  NotebookLMInActionAuthority="
        << state.notebookRole.inActionAuthority << '\n'
        << '\n'
        << "  SpecificationReady="
        << state.status.specificationReady << '\n'
        << "  CurrentBoundary="
        << state.status.currentBoundary.str() << '\n'
        << "  NextExpectedSegment="
        << state.status.nextExpectedSegment.str() << '\n'
        << "  ContinuationTarget="
        << state.status.continuationTarget.str() << '\n'
        << "}\n";

    if (!report.issues.empty()) {
        std::cerr
            << "VALIDATION_ISSUES\n"
            << "{\n";

        for (const auto& issue : report.issues) {
            std::cerr
                << "  ["
                << toString(issue.action)
                << "] "
                << toString(issue.code)
                << ": "
                << issue.message
                << '\n';
        }

        std::cerr << "}\n";
    }
}

} // namespace apo

int main(int argc, char** argv) {
    try {
        apo::APOLoadState state =
            (argc >= 2)
                ? apo::APOLoadState::fromWorkspaceManifest(argv[1])
                : apo::APOLoadState::production();

        const apo::ValidationReport report =
            state.selfInitialize();

        apo::printState(state, report);

        const bool success =
            state.initialized() &&
            state.executionOrder.complete() &&
            state.input == "META_SPEC_APO" &&
            state.parse == "PASS" &&
            state.type == "APO-Language" &&
            state.segmentLoaded ==
                apo::SegmentRange{
                    apo::SegmentBoundary{1, 0},
                    apo::SegmentBoundary{9, 12}
                } &&
            !state.syntheticState &&
            !state.missingState &&
            !state.narrativeInjection &&
            report.valid() &&
            state.omegaGate.survivalOmega == 12 &&
            state.omegaGate.omegaGlobal &&
            state.canonicalResult.omegaAllOne &&
            state.canonicalResult.FOmega.value &&
            !state.canonicalResult.fusionRejected &&
            state.status.specificationReady;

        return success
            ? EXIT_SUCCESS
            : EXIT_FAILURE;
    } catch (const std::exception& exception) {
        std::cerr
            << "APO_FATAL_ERROR: "
            << exception.what()
            << '\n';

        return EXIT_FAILURE;
    } catch (...) {
        std::cerr
            << "APO_FATAL_ERROR: unknown exception\n";

        return EXIT_FAILURE;
    }
}