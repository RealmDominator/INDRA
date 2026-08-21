"""In-memory NetworkX supply graph; PostgreSQL remains the source of truth."""
import networkx as nx


def build_supply_graph(suppliers, routes, ports, refineries) -> nx.DiGraph:
    graph = nx.DiGraph()
    port_country = {port.id: getattr(port, "country_id", None) for port in ports}
    for supplier in suppliers:
        graph.add_node(f"supplier:{supplier.id}", kind="supplier", entity=supplier)
    for route in routes:
        graph.add_node(f"route:{route.id}", kind="route", entity=route)
        graph.add_edge(f"port:{route.origin_port_id}", f"route:{route.id}")
        graph.add_edge(f"route:{route.id}", f"port:{route.dest_port_id}")
        for corridor_id in route.corridor_ids or []:
            graph.add_edge(f"corridor:{corridor_id}", f"route:{route.id}")
        for supplier in suppliers:
            if supplier.country_id and supplier.country_id == port_country.get(route.origin_port_id):
                graph.add_edge(f"supplier:{supplier.id}", f"route:{route.id}")
    for port in ports:
        graph.add_node(f"port:{port.id}", kind="port", entity=port)
    for refinery in refineries:
        graph.add_node(f"refinery:{refinery.id}", kind="refinery", entity=refinery)
        if refinery.port_id:
            graph.add_edge(f"port:{refinery.port_id}", f"refinery:{refinery.id}")
    return graph


def affected_refineries(graph: nx.DiGraph, corridor_id: int) -> list[int]:
    routes = [node for node in graph.successors(f"corridor:{corridor_id}") if node.startswith("route:")]
    result = set()
    for route in routes:
        for port in graph.successors(route):
            result.update(int(node.split(":", 1)[1]) for node in graph.successors(port) if node.startswith("refinery:"))
    return sorted(result)
