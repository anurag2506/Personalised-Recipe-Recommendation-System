import networkx as nx
import pandas as pd
import json

def clean_and_parse_json(json_str):
    try:
        json_str = json_str.strip()
        json_str = json_str.encode('utf-8', errors='ignore').decode('utf-8')
        details = json.loads(json_str)
        details = {k.replace(' ', '_').lower(): v for k, v in details.items()}
        return details
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"JSON parsing error: {e}")
        return None

class RecipeRecommendationSystem:
    def __init__(self, dataframe):
        self.df = dataframe
        self.graph = nx.Graph()
        self._clean_and_parse_json = clean_and_parse_json
        self._build_recipe_graph()

    def _build_recipe_graph(self):
        for i, row_i in self.df.iterrows():
            for j, row_j in self.df.iterrows():
                if i != j:
                    try:
                        details_i = self._clean_and_parse_json(row_i["info_json"])
                        details_j = self._clean_and_parse_json(row_j["info_json"])

                        if not details_i or not details_j:
                            continue

                        shared_ingredients = set(details_i.get("ingredients", [])) & set(details_j.get("ingredients", []))
                        ingredient_similarity = len(shared_ingredients)

                        prep_time_i = int(details_i.get("preparation_time", 0))
                        prep_time_j = int(details_j.get("preparation_time", 0))
                        prep_time_similarity = abs(prep_time_i - prep_time_j) <= 10

                        cuisine_similarity = details_i.get("specific_cuisine", "") == details_j.get("specific_cuisine", "")
                        dietary_similarity = details_i.get("dietary_category", "") == details_j.get("dietary_category", "")

                        similarity_score = (
                            ingredient_similarity +
                            (1 if prep_time_similarity else 0) +
                            (1 if cuisine_similarity else 0) +
                            (1 if dietary_similarity else 0)
                        )

                        if similarity_score > 0:
                            self.graph.add_node(row_i["item_name"], **details_i)
                            self.graph.add_node(row_j["item_name"], **details_j)

                            self.graph.add_edge(
                                row_i["item_name"],
                                row_j["item_name"],
                                weight=similarity_score
                            )

                    except Exception as e:
                        print(f"Error processing {row_i['item_name']} or {row_j['item_name']}: {e}")

    def get_recipe_nodes(self):
        return list(self.graph.nodes(data=True))

def recommend_recipes(recipe_nodes, user_preferences, top_n=5):
    recommendations = []
    for recipe_name, recipe_data in recipe_nodes:
        try:
            ingredient_match = len(
                set(user_preferences.get('ingredients', [])) &
                set(recipe_data.get('ingredients', []))
            ) / len(set(recipe_data.get('ingredients', [])))

            cuisine_match = user_preferences.get('cuisine', '') == recipe_data.get('specific_cuisine', '')
            dietary_match = user_preferences.get('dietary_preference', '') == recipe_data.get('dietary_category', '')

            time_match = abs(
                user_preferences.get('available_time', 0) -
                recipe_data.get('preparation_time', 0)
            ) <= 15

            final_score = (
                0.4 * ingredient_match +
                0.3 * cuisine_match +
                0.2 * dietary_match +
                0.1 * time_match
            ) * 100

            recommendations.append({
                'recipe_name': recipe_name,
                'match_score': round(final_score, 2),
                'details': {
                    'ingredients_match': f"{ingredient_match * 100:.1f}%",
                    'cuisine_match': f"{cuisine_match * 100:.1f}%",
                    'dietary_match': f"{dietary_match * 100:.1f}%",
                    'time_match': f"{time_match * 100:.1f}%",
                    'recipe_details': recipe_data
                }
            })
        except Exception as e:
            print(f"Error processing recommendation for {recipe_name}: {e}")

    return sorted(recommendations, key=lambda x: x['match_score'], reverse=True)[:top_n]