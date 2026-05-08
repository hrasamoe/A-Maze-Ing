_This project has been created as part of the 42 curriculum by hrasamoe, ny-araza_


#  DESCRIPTION

This project implements a maze solving algorithm using **Breadth First Search (BFS)** and **Deaph First Search (DFS)** to find the shortest path through a maze.
This project use MLX for rendering maze and for interaction with the user.

---

### STRUCTURE OF CONFIG FILE

<div>
  <table>
    <thead>
      <th>
        Name
      </th>
      <th>
        Property
      </th>
    </thead>
    <tbody>
      <tr>
        <td>WIDTH</td>
        <td>the size of the width maze</td>
      </tr>
      <tr>
        <td>HEIGHT</td>
        <td>the size of the height maze</td>
      </tr>
      <tr>
        <td>WINDOW_W</td>
        <td>the size of the width window</td>
      </tr>
      <tr>
        <td>WINDOW_H</td>
        <td>the size of the height window</td>
      </tr>
      <tr>
        <td>ENTRY</td>
        <td>the entry position (x, y)</td>
      </tr>
      <tr>
        <td>EXIT</td>
        <td>the exit position (x, y)</td>
      </tr>
      <tr>
        <td>OUTPUT_FILE</td>
        <td>the output file that save the maze solution</td>
      </tr>
      <tr>
        <td>PERFECT</td>
        <td>Toogle perfect maze (True or False)</td>
      </tr>
    </tbody>
  </table>
</div>

**Example**
<div>
  <table>
    <thead>
      <th>
        Name
      </th>
      <th>
        Property
      </th>
    </thead>
    <tbody>
      <tr>
        <td>WIDTH</td>
        <td>29</td>
      </tr>
      <tr>
        <td>HEIGHT</td>
        <td>16</td>
      </tr>
      <tr>
        <td>WINDOW_W</td>
        <td>1920</td>
      </tr>
      <tr>
        <td>WINDOW_H</td>
        <td>1000</td>
      </tr>
      <tr>
        <td>ENTRY</td>
        <td>5, 6</td>
      </tr>
      <tr>
        <td>EXIT</td>
        <td>28, 15</td>
      </tr>
      <tr>
        <td>OUTPUT_FILE</td>
        <td>maze_output.txt</td>
      </tr>
      <tr>
        <td>PERFECT</td>
        <td>True</td>
      </tr>
    </tbody>
  </table>
</div>
---

#  INSTRUCTION

### Clone the project

```bash
git clone <url_of_repo> Amazing
cd Amazing
```

### Usage

#### 1. Download the MLX library on intranet

**With virtual environment:**

```bash
# Install dependencies and package utils on this project
make install

# Check mypy and flake8
make lint-strict

# Launch the program
make run

# Build the package
make build

# clean the workflow, remove the cache of mypy and flake8
make clean

#remove the cache and venv on the project
make fclean
```

**Without virtual environment:**

```bash
pip install pydantic mlx-2.2-py3-none-any.whl
python3 a_maze_ing.py config.txt
```

---

#  RESOURCES

- [Breadth First Search or BFS for a Graph](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)
- [Depht First Search or DFS for a Graph](https://profound.academy/fr/algorithms-data-structures/algorithme-de-recherche-en-profondeur-dfs-Hfp3FggTTjqlsuiDf6az)
- [MLX initialisation an rendering](https://mlx-doc.netlify.app/)


###  AI USAGE

Claude was used to explain more details for our chosen algorithm and sometimes we used it to check how we can improve our approach on this project.  
Claude was used to expalin how to init **MLX** and use animation

---

#  ALGORITHM EXPLANATION

We use pydantic because it used for data validation and data parsing using Python type hints. It ensures that data structures like classes, dictionaries or API inputs contain valid and correctly typed data before being processed. Pydantic automatically converts and validates incoming data, helping developers write cleaner, more reliable code.

#### BFS Algorithm

A Breadth-First Search (BFS) generator on a maze creates a grid of paths by expanding outward from a starting point, exploring all neighboring cells at the current distance before moving further away. Using a Queue (FIFO - First-In-First-Out), the algorithm ensures that the maze is generated in a uniform, "bushy" manner
```
Start → [Queue] → Explore neighbors level by level → Goal 
```
#### BFS Algorithm

Depth-First Search (DFS) is a graph traversal algorithm that explores a path as far as possible before backtracking.
It starts at a starting vertex, visits an unexplored neighbor, and then continues moving from neighbor to neighbor.
When it reaches a vertex with no unvisited neighbors, it returns to the previous vertex to explore other possible paths.
This process continues until all reachable vertices have been visited or until a desired destination is found.
```
Start → Explore neighbors level by level → if not find neighbors -> return previews visited and find another path -> Goal 
```
**Revised Justification**
The maze generator is implemented as a reusable class in mazegen.*.py. It is designed to be exported as a .whl package, allowing it to be easily imported into other projects.

**Algorithm Choice:**
We utilize Breadth-First Search (BFS) and Depth-First Search (DFS) as they are the standard algorithms for graph traversal and pathfinding. Their popularity and logical simplicity make the codebase both efficient and accessible for educational purposes.




# CONTRIBUTIONS


<table>
  <tr>
    <td valign="top">
      <table>
        <tr>
          <td align="center" width="120">
            <img 
              src="https://cdn.intra.42.fr/users/824236a35151d016d755597d924388e6/hrasamoe.jpg" 
              alt="hrasamoe" 
              width="83"
              style="border: 2px solid #4a90e2; border-radius: 10%; box-shadow: 4px 4px 12px rgba(0,0,0,0.2);"
            /><br/>
            <strong>hrasamoe</strong>
          </td>
          <td valign="middle" style="padding-left: 20px;">
            <strong>BFS algorithm implementation & maze parser</strong><br/>
            <strong>Solve the Maze with BFS and get the path of it</strong><br/>
            <strong>Output the maze, the config and solution path on a file</strong><br/>
            <strong></strong>
          </td>
        </tr>
        <tr>
          <td align="center" width="120">
            <img 
              src="https://cdn.intra.42.fr/users/777c5c8ffe9379d1469c7bd695d90615/ny-araza.jpg" 
              alt="ny-araza" 
                          width="83"
              style="border: 2px solid #4a90e2; border-radius: 10%; box-shadow: 4px 4px 12px rgba(0,0,0,0.2);"
           /><br/>
            <strong>ny-araza</strong>
          </td>
          <td valign="middle" style="padding-left: 20px;">
             <strong>DFS algorithm implementation</strong><br/>
             <strong>Play Mode integration</strong><br/>
             <strong>Create the window with MLX and provide the visual render on it</strong>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>