#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <queue>
using namespace std;

unordered_map<string, vector<string>> adj; // adjacency list
unordered_set<string> nodes; // unique nodes

// Function to trim whitespace
string trim(const string &str) {
    size_t start = str.find_first_not_of(" \t\r\n");
    size_t end = str.find_last_not_of(" \t\r\n");
    return (start == string::npos || end == string::npos) ? "" : str.substr(start, end - start + 1);
}

// Adds bidirectional edge
void addEdge(string a, string b) {
    a = trim(a);
    b = trim(b);
    if (!a.empty() && !b.empty()) {
        adj[a].push_back(b);
        adj[b].push_back(a);
        nodes.insert(a);
        nodes.insert(b);
    }
}

void buildGraph(const string &filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cout << "Unable to open file.\n";
        return;
    }

    string line;
    while (getline(file, line)) {
        size_t dash = line.find(" - ");
        if (dash == string::npos) continue;

        string left = line.substr(0, dash);
        string right = line.substr(dash + 3);

        addEdge(left, right);
    }

    file.close();
}

// BFS traversal from a given node
void bfs(const string &start) {
    unordered_set<string> visited;
    queue<string> q;

    visited.insert(start);
    q.push(start);

    cout << "\nBFS Traversal from \"" << start << "\":\n";

    while (!q.empty()) {
        string current = q.front(); q.pop();
        cout << current << "\n";

        for (const string &neighbor : adj[current]) {
            if (!visited.count(neighbor)) {
                visited.insert(neighbor);
                q.push(neighbor);
            }
        }
    }
}

int main() {
    string filename = "hospital_data.txt"; // replace with your actual file name
    buildGraph(filename);

    cout << "Graph Built. Total Nodes: " << nodes.size() << "\n";

    string source;
    cout << "Enter starting hospital name or ID for BFS traversal:\n";
    getline(cin, source);
    source = trim(source);

    if (!nodes.count(source)) {
        cout << "Node not found in data.\n";
        return 0;
    }

    bfs(source);

    return 0;
}
