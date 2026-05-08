_This project has been created as part of the 42 curriculum by hrasamoe, ny-araza_

#  A-MAZE-ING

> Maze solving algorithm using Breadth First Search (BFS) to find the shortest path through a maze.

---

#  DESCRIPTION

This project implements a maze solving algorithm using **Breadth First Search (BFS)** to find the shortest path through a maze.

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
```

**Without virtual environment:**

```bash
pip install pydantic mlx-2.2-py3-none-any.whl
python3 a_maze_ing.py config.txt
```

---

#  RESOURCES

- [Breadth First Search or BFS for a Graph](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)

###  AI USAGE

Claude was used to explain more details for our chosen algorithm and sometimes we used it to check how we can improve our approach on this project.

---

#  ALGORITHM EXPLANATION

BFS is a graph traversal algorithm that explores all vertices at the present depth level before moving to vertices at the next depth level. This ensures finding the **shortest path** in an unweighted maze.

```
Start → [Queue] → Explore neighbors level by level → Goal ✅
```

---

# 👥 CONTRIBUTIONS


<table>
  <tr>
    <td valign="top">
      <table>
        <tr>
          <td align="center" width="120">
            <img 
              src="https://cdn.intra.42.fr/users/824236a35151d016d755597d924388e6/hrasamoe.jpg" 
              alt="hrasamoe" 
              width="100"
              style="border: 2px solid #4a90e2; border-radius: 12px; box-shadow: 4px 4px 12px rgba(0,0,0,0.2);"
            /><br/>
            <strong>hrasamoe</strong>
          </td>
          <td valign="middle" style="padding-left: 20px;">
            🗺️ <strong>hrasamoe</strong> — BFS algorithm implementation & maze parser
          </td>
        </tr>
        <tr>
          <td align="center" width="120">
            <img 
              src="https://cdn.intra.42.fr/users/777c5c8ffe9379d1469c7bd695d90615/ny-araza.jpg" 
              alt="ny-araza" 
              width="100"
              style="border: 2px solid #4a90e2; border-radius: 12px; box-shadow: 4px 4px 12px rgba(0,0,0,0.2);"
            /><br/>
            <strong>ny-araza</strong>
          </td>
          <td valign="middle" style="padding-left: 20px;">
            🎨 <strong>ny-araza</strong> — MLX rendering & visual path display
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>