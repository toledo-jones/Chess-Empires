# [DEBUG] Starting calculate_points_per_resource
# [DEBUG] Initial resource_count: {'gold': 100, 'wood': 584, 'quarry': 208}
# [DEBUG] Recalculated total_resources from values: 892
#
# [DEBUG] Processing resource: gold, count: 100
# [DEBUG] Scarcity for 'gold': 0.8879 (1 - (100 / 892))
# [DEBUG] Weight for 'gold': 2.5767 (1 + (0.8878923766816144 ** 2) * 2)
# [DEBUG] Base points for 'gold': 8.9200 (892 / 100)
# [DEBUG] Final points (rounded) for 'gold': 23 (8.92 * 2.5767057451386517)
# [DEBUG] Realistic count for 'gold': 100 (rounded 100 ** 1
# [DEBUG] Total points possible for 'gold': 2300 (23 * 100)
#
# [DEBUG] Processing resource: wood, count: 584
# [DEBUG] Scarcity for 'wood': 0.3453 (1 - (584 / 892))
# [DEBUG] Weight for 'wood': 1.2385 (1 + (0.3452914798206278 ** 2) * 2)
# [DEBUG] Base points for 'wood': 1.5274 (892 / 584)
# [DEBUG] Final points (rounded) for 'wood': 2 (1.5273972602739727 * 1.2384524120734381)
# [DEBUG] Realistic count for 'wood': 584 (rounded 584 ** 1
# [DEBUG] Total points possible for 'wood': 1168 (2 * 584)
#
# [DEBUG] Processing resource: quarry, count: 208
# [DEBUG] Scarcity for 'stone': 0.7668 (1 - (208 / 892))
# [DEBUG] Weight for 'stone': 2.1760 (1 + (0.7668161434977578 ** 2) * 2)
# [DEBUG] Base points for 'stone': 4.2885 (892 / 208)
# [DEBUG] Final points (rounded) for 'stone': 9 (4.288461538461538 * 2.1760139958575477)
# [DEBUG] Realistic count for 'stone': 208 (rounded 208 ** 1
# [DEBUG] Total points possible for 'stone': 1872 (9 * 208)

# [DEBUG] Final points_per_resource: {'gold': {'points': 23, 'available': 2300}, 'wood': {'points': 2, 'available': 1168}, 'stone': {'points': 9, 'available': 1872}}

total_resources = {'gold': 100, 'wood': 584, 'quarry': 208}

