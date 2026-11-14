#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <queue>
#include <functional>
#include <algorithm>

namespace py = pybind11;
using namespace std;

class Graph {
public:
    unordered_map<int, vector<int>> adj;

    unordered_set<int> visited;
    int active_node = -1;
    function<void()> on_step;

    int timer_idx = 0;
    unordered_map<int, int> number;
    unordered_map<int, int> lowlink;
    unordered_map<int, bool> on_stack;
    stack<int> st;
    vector<vector<int>> sccs;

    void set_callback(function<void()> cb) {
        on_step = cb;
    }

    void add_node(int u) {
        adj[u];
        if (on_step) on_step();
    }

    void add_edge(int u, int v, bool directed = false) {
        adj[u].push_back(v);
        if (!directed) {
            adj[v].push_back(u);
        } else if (adj.find(v) == adj.end()) {
            adj[v] = {};
        }
        if (on_step) on_step();
    }

    void bfs(int start_node) {
        visited.clear();
        queue<int> q;

        visited.insert(start_node);
        q.push(start_node);

        while (!q.empty()) {
            active_node = q.front();
            q.pop();

            if (on_step) on_step();

            for (int neighbor : adj[active_node]) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    q.push(neighbor);
                    if (on_step) on_step();
                }
            }
        }
        active_node = -1;
        if (on_step) on_step();
    }

    void strongconnect(int v) {
        number[v] = lowlink[v] = ++timer_idx;
        st.push(v);
        on_stack[v] = true;

        active_node = v;
        visited.insert(v);
        if (on_step) on_step();

        if (adj.count(v)) {
            for (int w : adj[v]) {
                if (number[w] == 0) {
                    strongconnect(w);
                    lowlink[v] = std::min(lowlink[v], lowlink[w]);

                    active_node = v;
                    if (on_step) on_step();
                } else if (number[w] < number[v] && on_stack[w]) {
                    lowlink[v] = std::min(lowlink[v], number[w]);
                }
            }
        }

        if (lowlink[v] == number[v]) {
            std::vector<int> current_scc;
            while (!st.empty() && number[st.top()] >= number[v]) {
                int w = st.top();
                st.pop();
                on_stack[w] = false;
                current_scc.push_back(w);
            }
            sccs.push_back(current_scc);
        }
    }

    vector<std::vector<int>> tarjan_scc() {
        timer_idx = 0;
        number.clear();
        lowlink.clear();
        on_stack.clear();
        visited.clear();
        active_node = -1;
        while (!st.empty()) st.pop();
        sccs.clear();

        std::unordered_set<int> all_nodes;
        for (const auto& par : adj) {
            all_nodes.insert(par.first);
            for (int w : par.second) {
                all_nodes.insert(w);
            }
        }

        for (int u : all_nodes) {
            if (number[u] == 0) {
                strongconnect(u);
            }
        }

        active_node = -1;
        if (on_step) on_step();

        std::reverse(sccs.begin(), sccs.end());
        return sccs;
    }
};

PYBIND11_MODULE(graph_anim, m) {
    py::class_<Graph>(m, "Graph")
        .def(py::init<>())
        .def("set_callback", &Graph::set_callback)
        .def("add_node", &Graph::add_node, py::arg("u"))
        .def("add_edge", &Graph::add_edge, py::arg("u"), py::arg("v"), py::arg("directed") = false)
        .def("bfs", &Graph::bfs)
        .def("strongconnect", &Graph::strongconnect, py::arg("v"))
        .def("tarjan_scc", &Graph::tarjan_scc)
        .def_readonly("adj", &Graph::adj)
        .def_readonly("visited", &Graph::visited)
        .def_readonly("active_node", &Graph::active_node);
}
