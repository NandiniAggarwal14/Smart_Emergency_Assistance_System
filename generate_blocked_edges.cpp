#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <algorithm>

int main() {
    std::ifstream infile("graph_edges.txt");
    std::ofstream outfile("blocked_edges.txt");

    if (!infile || !outfile) {
        std::cerr << "Error opening input or output file.\n";
        return 1;
    }

    std::vector<std::pair<std::string, std::string>> edges;
    std::string line;

    // Step 1: Load all edges
    while (std::getline(infile, line)) {
        if (line.empty()) continue;

        size_t sep_pos = line.find(" - ");
        size_t last_space = line.rfind(' ');

        if (sep_pos == std::string::npos || last_space == std::string::npos) continue;

        std::string node1 = line.substr(0, sep_pos);
        std::string node2 = line.substr(sep_pos + 3, last_space - sep_pos - 3);

        edges.emplace_back(node1, node2);
    }

    infile.close();

    // Step 2: Randomly shuffle and pick 3 edges
    std::srand(std::time(nullptr));
    std::random_shuffle(edges.begin(), edges.end());

    int num_blocked = std::min(50, (int)edges.size());  

    // Step 3: Write blocked edges
    for (int i = 0; i < num_blocked; ++i) {
        outfile << edges[i].first << " - " << edges[i].second << "\n";
    }

        std::ofstream activeFile("active_edges.txt");
    if (!activeFile) {
        std::cerr << "Error opening active_edges.txt for writing.\n";
        return 1;
    }

    for (int i = num_blocked; i < edges.size(); ++i) {
        activeFile << edges[i].first << " - " << edges[i].second << "\n";
    }

    activeFile.close();
    std::cout << "Remaining active edges written to active_edges.txt\n";

    outfile.close();
    std::cout << "Random blocked edges written to blocked_edges.txt\n";

    return 0;
}
