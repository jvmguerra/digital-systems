namespace py graphdb

typedef i32 int

exception ElementNotFoundException{ }

struct Vertex {
            1:int id,
            2:int color,
            3:int weight
}

// Direction: 1 for v2 to v1, 2 for v1 to v2, 0 for both
struct Edge {
            1:Vertex v1,
            2:Vertex v2,
            3:int weight,
            4:int direction
}

struct Graph {
            1:list<Vertex> vertexList,
            2:list<Edge> EdgesList,
}

service GraphCRUD {
        // Vertex CRUD
        void createVertex(1:Vertex vertex),
        Vertex readVertex(1:int id)  throws (1:ElementNotFoundException e),
        void updateVertex(1:Vertex vertex),
        void deleteVertex(1:int id),
        // Edges CRUD
        void createEdge(1:int v1, 2:int v2, 3:int weight, 4:int direction),
        Edge readEdge(1:int v1, 2:int v2)  throws (1:ElementNotFoundException e),
        void updateEdge(1:int v1, 2:int v2, 3:int weight, 4:int direction),
        void deleteEdge(1:int v1, 2:int v2),
        // Listings
        list<Edge> listVertexEdges(1:int vertex)  throws (1:ElementNotFoundException e),
        list<Vertex> listAdjacentVertex(1:int vertex)  throws (1:ElementNotFoundException e)
}