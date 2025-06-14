high_wood = {'gold': 100, 'wood': 584, 'quarry': 208}
high_gold = {'gold': 300, 'wood': 200, 'quarry': 542}


def calculate_points_per_resource(resource_count):
    """
    Calculates the points per resource based on the provided resource count and total resources.

    :param resource_count: The total number of resources.
    :return: A dictionary with resource names as keys and their points and availability as values.
    """
    points_per_resource: dict = {}
    total_resources = sum(resource_count.values())

    print(f"\n[DEBUG] Starting resource_count: {resource_count}")
    for resource, count in resource_count.items():
        # Normalize resource name
        if resource == "quarry":
            resource = "stone"

        # Skip zero-count resources
        if count <= 0:
            points_per_resource[resource] = {"points": 0, "available": 0}
            continue

        # Step 1: Scarcity
        scarcity = 1 - (count / total_resources)

        # Step 2: Weight based on scarcity (exaggerated by squaring)
        weight = 1 + (scarcity ** 2) * .005

        # Step 3: Base points
        base_points = total_resources / count
        points = round(base_points * weight)

        # Step 4: Nonlinear access curve to simulate realistic availability
        const = 1
        realistic_count = round(count ** const)

        total_points_possible = points * realistic_count

        points_per_resource[resource] = {
            "points"   : points,
            "available": total_points_possible,
        }

    print(f"\n[DEBUG] Final points_per_resource: {points_per_resource}\n")

calculate_points_per_resource(high_wood)
calculate_points_per_resource(high_gold)