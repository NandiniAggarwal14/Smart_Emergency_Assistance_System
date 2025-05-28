#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <map>
#include <vector>
#include <utility>

int main() {
    std::string filename = "graph_edges.txt";  
    std::ifstream infile(filename);

    if (!infile) {
        std::cerr << "Error opening file: " << filename << "\n";
        return 1;
    }

    // Graph: node1 -> vector of (node2, distance)
    std::map<std::string, std::vector<std::pair<std::string, double>>> graph;

    std::string line;
    while (std::getline(infile, line)) {
        if (line.empty()) continue;

        // Find " - " separator
        size_t sep_pos = line.find(" - ");
        if (sep_pos == std::string::npos) {
            std::cerr << "Line format error (missing ' - '): " << line << "\n";
            continue;
        }

        std::string node1 = line.substr(0, sep_pos);
        std::string rest = line.substr(sep_pos + 3);  // after " - "

        // Now, rest contains: node2 + " " + distance

        // To separate node2 and distance:
        // Find last space in rest (distance is after last space)
        size_t last_space = rest.rfind(' ');
        if (last_space == std::string::npos) {
            std::cerr << "Line format error (missing distance): " << line << "\n";
            continue;
        }

        std::string node2 = rest.substr(0, last_space);
        std::string distance_str = rest.substr(last_space + 1);

        double distance;
        try {
            distance = std::stod(distance_str);
        } catch (const std::exception& e) {
            std::cerr << "Error converting distance to number: " << distance_str << " in line: " << line << "\n";
            continue;
        }

        // Add edge to graph
        graph[node1].push_back(std::make_pair(node2, distance));
    }

    infile.close();

    // Print some data to check
    std::cout << "Graph loaded:\n";
    for (const auto& entry : graph) {
        std::cout << entry.first << " -> ";
        for (const auto& dest : entry.second) {
            std::cout << "(" << dest.first << ", " << dest.second << ") ";
        }
        std::cout << "\n";
    }

    return 0;
}
