import random
import json
from typing import List, Dict


class Meal:
        def __init__(self, name: str, ingredients: List[str], prep_time: int, servings: int, nutrition: Dict[str, int], meal_type: str, dietary_preferences: List[str]):
            self.name = name
            self.ingredients = ingredients
            self.prep_time = prep_time
            self.servings = servings
            self.nutrition = nutrition  # Prints out the amount of calories, protein, carbs, and fat in each meal
            self.meal_type = meal_type  # Prints the 3 meals, breakfast, lunch, dinner
            self.dietary_preferences = [pref.strip().lower() for pref in dietary_preferences]


        def __str__(self):
            return (
                f"{self.name} ({self.meal_type})\n"
                f"  Calories: {self.nutrition['calories']} kcal, Protein: {self.nutrition['protein']}g, "
                f"Carbs: {self.nutrition['carbs']}g, Fat: {self.nutrition['fat']}g\n"
                f"  Ingredients: {', '.join(self.ingredients)}"
            )


class User:
        def __init__(self, dietary_preferences: List[str], restrictions: List[str], caloric_needs: int = None):
            self.dietary_preferences = [pref.strip().lower() for pref in dietary_preferences]  
            self.restrictions = [restriction.strip().lower() for restriction in restrictions]  
            self.caloric_needs = caloric_needs
            self.meal_plan = []
            self.favorites = [] 
            self.excluded_meals = []
        
        def __str__(self):
            return f"Preferences: {self.dietary_preferences}, Restrictions: {self.restrictions}, Caloric Needs: {self.caloric_needs}"

        def save_favorite(self, meal):
                if meal not in self.favorites:
                        self.favorites.append(meal)
                        print(f"{meal} added to Favorites!")
                else:
                        print(f"{meal} is already in Favorites.")
                        
        def exclude_meal(self, meal):
                if meal not in self.excluded_meals:
                        self.excluded_meals.append(meal)
                        print(f"{meal} added to Excluded Meals.")
                else:
                        print(f"{meal} is already in Excluded Meals.")

class MealPlanner:
        def __init__(self):
            self.user = None
            self.meals = self.load_meals_from_json([  # Two paths for the json files
                "meal_planner_recipes.json",
                "meal_planner_50_meals.json"
            ])

        def load_meals_from_json(self, file_paths):
            meals = []
            for file_path in file_paths:
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        for recipe in data["recipes"]:
                            meal = Meal(
                                name=recipe["name"],
                                ingredients=recipe["ingredients"],
                                prep_time=recipe.get("prep_time", 0),
                                servings=recipe.get("servings", 1),
                                nutrition=recipe["nutrition"],
                                meal_type=recipe["meal_type"].strip().lower(),
                                dietary_preferences=recipe["dietary_preferences"]
                            )
                            meals.append(meal)
                except FileNotFoundError:
                    print(f"Error: File not found - {file_path}")
            return meals

        def get_user_preferences(self):
            dietary_preferences = input("Enter dietary preferences (none, vegan, gluten-free): ").split(", ")
            restrictions = input("Enter any food restrictions (e.g., no nuts, no dairy): ").split(", ")
            caloric_needs = input("Enter daily caloric needs (optional, press Enter to skip): ")
            caloric_needs = int(caloric_needs) if caloric_needs else None
            self.user = User(dietary_preferences, restrictions, caloric_needs)
            print(f"User preferences set: {self.user}")

        def generate_weekly_plan(self):
            if not self.user:
                print("User preferences not set. Please set preferences first.")
                return

            self.user.meal_plan = []  # Clear any previous meal plan
            all_meals = random.sample(self.meals, len(self.meals))  # Shuffle meals to maximize variety
            used_meals = set()  # Track globally used meals across the week

            for day in range(7):  # Displays the meal plan for 1 week, 7 days
                daily_meals = []
                daily_calories = 0  # Tracks total calories for the day
                for meal_type in ["breakfast", "lunch", "dinner"]:
                    suitable_meals = [
                        meal for meal in all_meals
                        if meal.meal_type == meal_type and
                        # Check if meal matches dietary preferences or "none" (default allows all)
                        (not self.user.dietary_preferences or "none" in self.user.dietary_preferences or
                         any(pref in meal.dietary_preferences for pref in self.user.dietary_preferences)) and
                        # Ensure meal does not contain restricted ingredients
                        (not self.user.restrictions or
                         all(restriction not in meal.ingredients for restriction in self.user.restrictions)) and
                        meal.name not in used_meals and 
                        meal.name not in self.user.excluded_meals # Ensure global uniqueness and excluded meals
                    ]
                    print(f"Checking meals for {meal_type} on day {day + 1}...")
                    print(f"Total meals: {len(all_meals)}, Suitable meals: {len(suitable_meals)}")

                    if suitable_meals:
                        selected_meal = random.choice(suitable_meals)
                        meal_calories = selected_meal.nutrition['calories']

                        # Check if adding this meal exceeds daily caloric limit
                        if self.user.caloric_needs and (daily_calories + meal_calories <= self.user.caloric_needs):
                            daily_meals.append(selected_meal)
                            daily_calories += meal_calories
                            used_meals.add(selected_meal.name)
                    else:
                        print(f"Warning: No suitable {meal_type} found for day {day + 1}.")
                        daily_meals.append(None)  # Add placeholder for missing meal

                self.user.meal_plan.append(daily_meals)

            print("Weekly meal plan generated successfully!")

        def display_meal_plan(self):
            if not self.user or not self.user.meal_plan:
                print("Meal plan is empty. Generate a plan first.")
                return

            print("\nGenerated Weekly Meal Plan:")
            for i, day_meals in enumerate(self.user.meal_plan, start=1):
                print(f"Day {i}:")
                for meal in day_meals:
                    if meal:
                        print(f" - {meal}")
                    else:
                        print(" - No suitable meal found for this slot.")
                print()
                    
        def add_favorite_meal(self):
            if not self.user:
                print("User preferences not set. Please set preferences first.")
                return
            meal_name = input("Enter the name of the meal to add to favorites: ").strip()
            meal = next((m for m in self.meals if m.name.lower() == meal_name.lower()), None)
            if meal:
                self.user.save_favorite(meal)  
            else: 
                print("Meal not found. Please try again.")

        def add_excluded_meal(self):
            if not self.user:
                print("User preferences not set. Please set preferences first.")
                return
            meal_name = input("Enter the name of the meal to exlude: ").strip()
            meal = next((m for m in self.meals if m.name.lower() == meal_name.lower()), None)
            if meal:
                self.user.exclude_meal(meal)  
            else: 
                print("Meal not found. Please try again.")

        def view_favorites(self):
            if not self.user or not self.user.meal_plan:
                print("No favorite meals saved yet.")
                return
            print("\nYour Favorite Meals:")
            for meal in self.user.favorites:
                print(f"{meal}")

        
        def display_menu(self): #Meal Planner Main Menu
            while True:
                print("\nMeal Planner Menu:")
                print("1. Set Preferences and Restrictions")
                print("2. Generate Weekly Meal Plan")
                print("3. View Meal Plan")
                print("4. Add Favorite Meal")
                print("5. Exclude Meal")
                print("6. View Favorites")
                print("7. Quit")

                choice = input("Choose an option: ")
                if choice == "1":
                    self.get_user_preferences()
                elif choice == "2":
                    self.generate_weekly_plan()
                elif choice == "3":
                    self.display_meal_plan()
                elif choice == "4":
                    self.add_favorite_meal()
                elif choice == "5":
                    self.add_excluded_meal()
                elif choice == "6":
                    self.view_favorites()
                elif choice == "7":
                    print("Thank you for using the Meal Planner. Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")


if __name__ == "__main__":
        planner = MealPlanner()
        planner.display_menu()
