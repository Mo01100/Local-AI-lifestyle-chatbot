"""
eval_dataset.py
================
Curated evaluation dataset for the Health AI Chatbot RAG system.
Contains 30 question–answer–context–ground_truth tuples for RAGAS evaluation.

Domains:
  - nutrition      (10 questions)
  - exercise       (10 questions)
  - mental_health  (10 questions)

Usage:
  from evaluation.eval_dataset import load_eval_dataset
  dataset = load_eval_dataset(pipeline)  # auto-retrieves contexts via RAG
"""

import sys
from pathlib import Path

# Allow imports from the scripts/ directory
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

# ─────────────────────────────────────────────────────────────
#  GROUND-TRUTH Q&A PAIRS
#  Each entry has:
#    question     : the user question in English
#    ground_truth : ideal correct answer (used for correctness/recall)
#    domain       : ChromaDB domain to restrict retrieval (optional)
# ─────────────────────────────────────────────────────────────
EVAL_QUESTIONS = [
    {
        "question": "What are good sources of protein for a vegetarian diet?",
        "ground_truth": "Lentils, chickpeas, tofu, tempeh, edamame, Greek yogurt, quinoa, and nuts.",
        "domain": "nutrition",
    },
    {
        "question": "How many calories are in a large boiled egg?",
        "ground_truth": "Approximately 78 calories, with 6g protein.",
        "domain": "nutrition",
    },
    {
        "question": "What foods are high in omega-3 fatty acids?",
        "ground_truth": "Salmon, mackerel, flaxseeds, chia seeds, and walnuts.",
        "domain": "nutrition",
    },
    {
        "question": "What is the difference between simple and complex carbohydrates?",
        "ground_truth": "Simple carbs digest quickly causing sugar spikes; complex carbs digest slowly providing sustained energy.",
        "domain": "nutrition",
    },
    {
        "question": "How much water should I drink per day?",
        "ground_truth": "About 2-3 litres (8-10 cups) daily for adults.",
        "domain": "nutrition",
    },
    {
        "question": "What are the health benefits of eating fiber?",
        "ground_truth": "Supports digestive health, lowers cholesterol, stabilizes blood sugar, and promotes satiety.",
        "domain": "nutrition",
    },
    {
        "question": "What is the glycemic index?",
        "ground_truth": "A measure of how quickly a food raises blood sugar levels.",
        "domain": "nutrition",
    },
    {
        "question": "Can you suggest a healthy high-protein breakfast?",
        "ground_truth": "Greek yogurt with berries, scrambled eggs with vegetables, or a protein smoothie.",
        "domain": "nutrition",
    },
    {
        "question": "What vitamins are important for bone health?",
        "ground_truth": "Calcium, vitamin D, magnesium, and vitamin K2.",
        "domain": "nutrition",
    },
    {
        "question": "What should I eat before a workout for energy?",
        "ground_truth": "Easily digestible carbohydrates like a banana or oatmeal 1-3 hours before.",
        "domain": "nutrition",
    },
    {
        "question": "What is the recommended daily intake of sugar?",
        "ground_truth": "No more than 36g for men and 25g for women per day.",
        "domain": "nutrition",
    },
    {
        "question": "Are artificial sweeteners safe?",
        "ground_truth": "Most FDA-approved artificial sweeteners are safe in moderation.",
        "domain": "nutrition",
    },
    {
        "question": "What are the benefits of a Mediterranean diet?",
        "ground_truth": "Promotes heart health and emphasizes healthy fats, whole grains, and lean proteins.",
        "domain": "nutrition",
    },
    {
        "question": "Is dietary cholesterol bad for you?",
        "ground_truth": "For most people, it has minimal impact on blood cholesterol compared to saturated fats.",
        "domain": "nutrition",
    },
    {
        "question": "What is gluten?",
        "ground_truth": "A protein found in wheat, barley, and rye.",
        "domain": "nutrition",
    },
    {
        "question": "How much protein is in a chicken breast?",
        "ground_truth": "A 3-ounce serving contains about 26 grams of protein.",
        "domain": "nutrition",
    },
    {
        "question": "What are probiotics?",
        "ground_truth": "Live bacteria and yeasts good for the digestive system.",
        "domain": "nutrition",
    },
    {
        "question": "What is intermittent fasting?",
        "ground_truth": "An eating pattern cycling between periods of fasting and eating.",
        "domain": "nutrition",
    },
    {
        "question": "Are all fats bad?",
        "ground_truth": "No, unsaturated fats are healthy while trans fats are harmful.",
        "domain": "nutrition",
    },
    {
        "question": "Why is hydration important?",
        "ground_truth": "Necessary for cellular processes and flushing toxins.",
        "domain": "nutrition",
    },
    {
        "question": "Should I take a multivitamin?",
        "ground_truth": "Helpful to fill nutritional gaps if your diet isn't perfectly balanced.",
        "domain": "nutrition",
    },
    {
        "question": "What is a calorie deficit?",
        "ground_truth": "Consuming fewer calories than you burn, leading to weight loss.",
        "domain": "nutrition",
    },
    {
        "question": "What are macros?",
        "ground_truth": "Carbohydrates, proteins, and fats.",
        "domain": "nutrition",
    },
    {
        "question": "Is fruit juice healthy?",
        "ground_truth": "Whole fruit is better due to fiber; juice often concentrates sugar.",
        "domain": "nutrition",
    },
    {
        "question": "Why eat carbs before a game?",
        "ground_truth": "Carbohydrates provide the fastest source of energy.",
        "domain": "nutrition",
    },
    {
        "question": "What happens if I eat too much salt?",
        "ground_truth": "Can lead to high blood pressure and heart disease.",
        "domain": "nutrition",
    },
    {
        "question": "What is veganism?",
        "ground_truth": "Excludes all animal products from the diet.",
        "domain": "nutrition",
    },
    {
        "question": "What is the keto diet?",
        "ground_truth": "A low-carb, high-fat diet.",
        "domain": "nutrition",
    },
    {
        "question": "Can I get calcium without dairy?",
        "ground_truth": "Yes, from leafy greens, fortified milks, and almonds.",
        "domain": "nutrition",
    },
    {
        "question": "What are water-soluble vitamins?",
        "ground_truth": "Vitamin C and B-complex vitamins.",
        "domain": "nutrition",
    },
    {
        "question": "How long do you boil an egg for a soft yolk?",
        "ground_truth": "About 6 to 7 minutes.",
        "domain": "nutrition",
    },
    {
        "question": "What's the best way to cook asparagus?",
        "ground_truth": "Roasting at 400F with olive oil, salt, and pepper for 10-15 minutes.",
        "domain": "nutrition",
    },
    {
        "question": "How do you make a basic vinaigrette?",
        "ground_truth": "Whisk together 3 parts oil, 1 part vinegar, mustard, salt, and pepper.",
        "domain": "nutrition",
    },
    {
        "question": "What temperature should chicken be cooked to?",
        "ground_truth": "Chicken should reach an internal temperature of 165°F (74°C).",
        "domain": "nutrition",
    },
    {
        "question": "How do you keep avocado from turning brown?",
        "ground_truth": "Squeeze lemon or lime juice over the exposed flesh or store it in an airtight container.",
        "domain": "nutrition",
    },
    {
        "question": "What is blanching?",
        "ground_truth": "Briefly boiling vegetables and then immediately plunging them into ice water to stop cooking.",
        "domain": "nutrition",
    },
    {
        "question": "How long should you let steak rest after cooking?",
        "ground_truth": "About 5-10 minutes to let the juices redistribute.",
        "domain": "nutrition",
    },
    {
        "question": "What's a good substitute for buttermilk?",
        "ground_truth": "One cup of milk combined with one tablespoon of lemon juice or white vinegar.",
        "domain": "nutrition",
    },
    {
        "question": "How do you properly dice an onion?",
        "ground_truth": "Cut in half, peel, make horizontal slices, then vertical slices, and finally chop across.",
        "domain": "nutrition",
    },
    {
        "question": "What is the secret to fluffy pancakes?",
        "ground_truth": "Don't overmix the batter; lumpy batter is fine.",
        "domain": "nutrition",
    },
    {
        "question": "What ratio of water to white rice should be used?",
        "ground_truth": "Typically 2 parts water to 1 part rice.",
        "domain": "nutrition",
    },
    {
        "question": "How do you make a roux?",
        "ground_truth": "Cook equal parts flour and fat (like butter) over medium heat.",
        "domain": "nutrition",
    },
    {
        "question": "Can you freeze fresh spinach?",
        "ground_truth": "Yes, but it's best to blanch it first before freezing.",
        "domain": "nutrition",
    },
    {
        "question": "What does 'al dente' mean?",
        "ground_truth": "Cooked so as to be still firm when bitten, usually referring to pasta.",
        "domain": "nutrition",
    },
    {
        "question": "What is a mirepoix?",
        "ground_truth": "A flavor base made from cooked, diced vegetables, usually onions, carrots, and celery.",
        "domain": "nutrition",
    },
    {
        "question": "How to prevent pasta from sticking together?",
        "ground_truth": "Use plenty of boiling water and stir occasionally during the first few minutes.",
        "domain": "nutrition",
    },
    {
        "question": "What can I use instead of baking powder?",
        "ground_truth": "A mixture of baking soda and an acid like cream of tartar or yogurt.",
        "domain": "nutrition",
    },
    {
        "question": "How to tell if a watermelon is ripe?",
        "ground_truth": "It should feel heavy, have a hollow sound when tapped, and have a yellow field spot.",
        "domain": "nutrition",
    },
    {
        "question": "What is the best type of potato for mashed potatoes?",
        "ground_truth": "Russet or Yukon Gold potatoes.",
        "domain": "nutrition",
    },
    {
        "question": "How to safely thaw frozen chicken?",
        "ground_truth": "In the refrigerator, in cold water (changed every 30 mins), or in the microwave.",
        "domain": "nutrition",
    },
    {
        "question": "What is the difference between baking soda and baking powder?",
        "ground_truth": "Baking soda needs an acid to activate; baking powder already contains the acid.",
        "domain": "nutrition",
    },
    {
        "question": "How do you caramelize onions?",
        "ground_truth": "Cook slowly over low heat with butter or oil until they turn deep brown and sweet.",
        "domain": "nutrition",
    },
    {
        "question": "What is cross-contamination?",
        "ground_truth": "The transfer of harmful bacteria from raw food (like meat) to ready-to-eat food.",
        "domain": "nutrition",
    },
    {
        "question": "How to properly store fresh herbs?",
        "ground_truth": "Trim stems and place in a glass of water in the fridge, or wrap loosely in a damp paper towel.",
        "domain": "nutrition",
    },
    {
        "question": "What can replace eggs in a vegan recipe?",
        "ground_truth": "Flaxseed meal with water, applesauce, or mashed bananas.",
        "domain": "nutrition",
    },
    {
        "question": "How to peel garlic easily?",
        "ground_truth": "Crush the clove slightly with the flat side of a knife, and the skin will slip off.",
        "domain": "nutrition",
    },
    {
        "question": "What's the main ingredient in hummus?",
        "ground_truth": "Chickpeas (garbanzo beans).",
        "domain": "nutrition",
    },
    {
        "question": "How long do cooked leftovers last in the fridge?",
        "ground_truth": "Generally 3 to 4 days.",
        "domain": "nutrition",
    },
    {
        "question": "What are the common ingredients in pesto?",
        "ground_truth": "Fresh basil, garlic, pine nuts, olive oil, and Parmesan cheese.",
        "domain": "nutrition",
    },
    {
        "question": "What's the easiest way to shred chicken?",
        "ground_truth": "Using two forks to pull it apart or using a hand mixer on low speed.",
        "domain": "nutrition",
    },
    {
        "question": "How do you thicken a soup or stew?",
        "ground_truth": "Add a cornstarch slurry, a roux, or puree beans/potatoes into the broth.",
        "domain": "nutrition",
    },
    {
        "question": "What does folding mean in baking?",
        "ground_truth": "Gently combining a light, airy mixture into a heavier mixture without deflating it.",
        "domain": "nutrition",
    },
    {
        "question": "How do you temper chocolate?",
        "ground_truth": "Heating and cooling it to precise temperatures so it sets with a glossy finish and snap.",
        "domain": "nutrition",
    },
    {
        "question": "What's a healthy alternative to mayonnaise in chicken salad?",
        "ground_truth": "Plain Greek yogurt or mashed avocado.",
        "domain": "nutrition",
    },
    {
        "question": "How do you clean leeks?",
        "ground_truth": "Slice them in half lengthwise and rinse under cold water to wash out the dirt between layers.",
        "domain": "nutrition",
    },
    {
        "question": "How should you store tomatoes?",
        "ground_truth": "At room temperature, away from direct sunlight; refrigeration ruins their texture.",
        "domain": "nutrition",
    },
    {
        "question": "What is deglazing?",
        "ground_truth": "Adding liquid (like wine or broth) to a hot pan to unstick browned flavor bits from the bottom.",
        "domain": "nutrition",
    },
    {
        "question": "What is the secret to a good grilled cheese?",
        "ground_truth": "Using a mix of melting cheeses and spreading mayo or butter on the outside bread slices.",
        "domain": "nutrition",
    },
    {
        "question": "How do you quickly ripen an avocado?",
        "ground_truth": "Place it in a brown paper bag with an apple or banana for a day or two.",
        "domain": "nutrition",
    },
    {
        "question": "What's the difference between broiling and baking?",
        "ground_truth": "Broiling uses intense direct heat from above, while baking surrounds the food with hot air.",
        "domain": "nutrition",
    },
    {
        "question": "How to make homemade vegetable broth?",
        "ground_truth": "Simmer onion, carrot, celery, garlic, and herb scraps in water for about an hour.",
        "domain": "nutrition",
    },
    {
        "question": "What can I substitute for soy sauce?",
        "ground_truth": "Tamari (for gluten-free), coconut aminos, or Worcestershire sauce.",
        "domain": "nutrition",
    },
    {
        "question": "How do you prevent a pie crust from shrinking?",
        "ground_truth": "Let the dough rest/chill before baking and use pie weights when blind baking.",
        "domain": "nutrition",
    },
    {
        "question": "What makes a cake dense instead of fluffy?",
        "ground_truth": "Overmixing the batter, which develops too much gluten, or using expired leavening agents.",
        "domain": "nutrition",
    },
    {
        "question": "How do you make a quick tomato sauce?",
        "ground_truth": "Sauté garlic in olive oil, add crushed canned tomatoes, simmer with basil and salt.",
        "domain": "nutrition",
    },
    {
        "question": "Which oil is best for deep frying?",
        "ground_truth": "An oil with a high smoke point like canola, peanut, or vegetable oil.",
        "domain": "nutrition",
    },
    {
        "question": "How do you know when salmon is cooked?",
        "ground_truth": "It flakes easily with a fork and becomes opaque pink.",
        "domain": "nutrition",
    },
    {
        "question": "What is a bain-marie?",
        "ground_truth": "A hot-water bath used for cooking delicate foods like custards or melting chocolate slowly.",
        "domain": "nutrition",
    },
    {
        "question": "How do you stop apples from browning after cutting?",
        "ground_truth": "Toss the slices in a little lemon juice or salt water.",
        "domain": "nutrition",
    },
    {
        "question": "What is quinoa?",
        "ground_truth": "A gluten-free seed that is cooked and eaten like a grain, packed with complete protein.",
        "domain": "nutrition",
    },
    {
        "question": "How is tofu made?",
        "ground_truth": "By curdling fresh soy milk and pressing the curds into block forms.",
        "domain": "nutrition",
    },
    {
        "question": "What can I make with overripe bananas?",
        "ground_truth": "Banana bread, smoothies, or mashed into oatmeal.",
        "domain": "nutrition",
    },
    {
        "question": "How to reduce the acidity of tomato sauce?",
        "ground_truth": "Add a pinch of sugar or a splash of milk/cream.",
        "domain": "nutrition",
    },
    {
        "question": "What is the difference between green and red bell peppers?",
        "ground_truth": "Red peppers are fully ripened green peppers, making them sweeter and higher in vitamin C.",
        "domain": "nutrition",
    },
    {
        "question": "How to make a simple salad dressing?",
        "ground_truth": "Olive oil, lemon juice or vinegar, salt, pepper, and a dash of Dijon mustard.",
        "domain": "nutrition",
    },
    {
        "question": "What is seitan made from?",
        "ground_truth": "Vital wheat gluten.",
        "domain": "nutrition",
    },
    {
        "question": "How do you properly wash mushrooms?",
        "ground_truth": "Wipe them with a damp paper towel instead of soaking them, as they absorb water like a sponge.",
        "domain": "nutrition",
    },
    {
        "question": "What is the maillard reaction?",
        "ground_truth": "A chemical reaction between amino acids and reducing sugars that gives browned food its distinctive flavor.",
        "domain": "nutrition",
    },
    {
        "question": "How do you keep cookies soft?",
        "ground_truth": "Store them in an airtight container with a slice of bread.",
        "domain": "nutrition",
    },
    {
        "question": "What's a quick way to peel ginger?",
        "ground_truth": "Scrape the skin off using the edge of a spoon.",
        "domain": "nutrition",
    },
    {
        "question": "How long should you boil potatoes for mashing?",
        "ground_truth": "About 15 to 20 minutes until fork-tender.",
        "domain": "nutrition",
    },
    {
        "question": "What is ghee?",
        "ground_truth": "Clarified butter commonly used in Indian cooking, with the milk solids removed.",
        "domain": "nutrition",
    },
    {
        "question": "How to make scrambled eggs fluffy?",
        "ground_truth": "Whisk vigorously before cooking and cook over medium-low heat while gently folding them.",
        "domain": "nutrition",
    },
    {
        "question": "What to do if a dish is too salty?",
        "ground_truth": "Add an acid (like lemon juice), a sweetener, or unsalted bulk (like potatoes) to balance it.",
        "domain": "nutrition",
    },
    {
        "question": "What is nutritional yeast?",
        "ground_truth": "An inactivated yeast used as a condiment, prized for its cheesy flavor and B vitamins.",
        "domain": "nutrition",
    },
    {
        "question": "How do you cook steel-cut oats?",
        "ground_truth": "Simmer in water or milk for 20-30 minutes, stirring occasionally.",
        "domain": "nutrition",
    },
    {
        "question": "What's the base of a traditional French onion soup?",
        "ground_truth": "Slowly caramelized onions and beef broth.",
        "domain": "nutrition",
    },
    {
        "question": "How to make homemade croutons?",
        "ground_truth": "Cube stale bread, toss with olive oil and herbs, and bake until crispy.",
        "domain": "nutrition",
    },
    {
        "question": "What is EVOO?",
        "ground_truth": "Extra Virgin Olive Oil.",
        "domain": "nutrition",
    },
    {
        "question": "How do you tell if an egg is fresh?",
        "ground_truth": "Place it in water; fresh eggs sink and lay flat, while old eggs float.",
        "domain": "nutrition",
    },
    {
        "question": "What primary muscles are targeted by the bench press?",
        "ground_truth": "The pectoralis major (chest), anterior deltoids (front shoulders), and triceps.",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a proper barbell squat?",
        "ground_truth": "Keep chest up, back straight, bend at the knees and hips, lowering your body until thighs are parallel to the floor, then push back up.",
        "domain": "exercise",
    },
    {
        "question": "What is the difference between a hammer curl and a standard bicep curl?",
        "ground_truth": "A hammer curl uses a neutral grip (palms facing each other), focusing more on the brachialis and brachioradialis, while a standard curl uses an underhand grip.",
        "domain": "exercise",
    },
    {
        "question": "What are the benefits of cardiovascular exercise?",
        "ground_truth": "Improves heart health, increases lung capacity, aids in weight loss, and reduces stress.",
        "domain": "exercise",
    },
    {
        "question": "Which muscles does a plank strengthen?",
        "ground_truth": "The transversus abdominis, rectus abdominis, obliques, and shoulders.",
        "domain": "exercise",
    },
    {
        "question": "What is a deadlift?",
        "ground_truth": "A compound weight training exercise in which a loaded barbell is lifted off the ground to the level of the hips, then lowered.",
        "domain": "exercise",
    },
    {
        "question": "How do you do a pull-up?",
        "ground_truth": "Hang from a pull-up bar with an overhand grip, pull your body up until your chin clears the bar, and lower yourself back down with control.",
        "domain": "exercise",
    },
    {
        "question": "What is HIIT?",
        "ground_truth": "High-Intensity Interval Training involves short bursts of intense exercise alternated with low-intensity recovery periods.",
        "domain": "exercise",
    },
    {
        "question": "How often should you rest between strength training workouts for the same muscle group?",
        "ground_truth": "Generally 48 hours is recommended to allow for adequate muscle recovery.",
        "domain": "exercise",
    },
    {
        "question": "What muscles does a lunge work?",
        "ground_truth": "Quadriceps, hamstrings, glutes, and calves.",
        "domain": "exercise",
    },
    {
        "question": "What is the purpose of a warm-up before exercising?",
        "ground_truth": "To gradually increase heart rate, improve blood flow to muscles, and reduce the risk of injury.",
        "domain": "exercise",
    },
    {
        "question": "What is progressive overload?",
        "ground_truth": "Gradually increasing the weight, frequency, or number of repetitions in your strength training routine to continuously challenge the muscles.",
        "domain": "exercise",
    },
    {
        "question": "How many minutes of moderate aerobic exercise are recommended per week?",
        "ground_truth": "At least 150 minutes per week, according to major health guidelines.",
        "domain": "exercise",
    },
    {
        "question": "What is a compound exercise?",
        "ground_truth": "An exercise that works multiple muscle groups and joints at the same time, such as squats or deadlifts.",
        "domain": "exercise",
    },
    {
        "question": "What is an isolation exercise?",
        "ground_truth": "An exercise that targets a single muscle group and involves only one joint, such as a bicep curl.",
        "domain": "exercise",
    },
    {
        "question": "What is the difference between aerobic and anaerobic exercise?",
        "ground_truth": "Aerobic exercise requires steady oxygen (like running), while anaerobic involves quick bursts of energy without relying on oxygen (like sprinting or heavy lifting).",
        "domain": "exercise",
    },
    {
        "question": "How do you do a burpee?",
        "ground_truth": "Start standing, drop into a squat, kick your feet back to a plank, do a push-up, jump your feet back to a squat, and jump up.",
        "domain": "exercise",
    },
    {
        "question": "What muscles are worked during a Romanian Deadlift (RDL)?",
        "ground_truth": "Hamstrings, glutes, and lower back erectors.",
        "domain": "exercise",
    },
    {
        "question": "What is DOMS?",
        "ground_truth": "Delayed Onset Muscle Soreness is the muscle pain and stiffness felt 24 to 72 hours after unaccustomed or strenuous exercise.",
        "domain": "exercise",
    },
    {
        "question": "Why is stretching important after a workout?",
        "ground_truth": "It helps improve flexibility, reduces muscle tension, and brings your heart rate down gradually.",
        "domain": "exercise",
    },
    {
        "question": "What is the Romanian twist?",
        "ground_truth": "Likely referring to the Russian twist, a core exercise that involves rotating the torso from side to side to engage the obliques.",
        "domain": "exercise",
    },
    {
        "question": "What makes a Bulgarian split squat different from a regular lunge?",
        "ground_truth": "The rear foot is elevated on a bench or block, which increases the range of motion and places more load on the front leg.",
        "domain": "exercise",
    },
    {
        "question": "What does a lat pulldown target?",
        "ground_truth": "The latissimus dorsi muscles in the middle back, as well as the biceps and rear deltoids.",
        "domain": "exercise",
    },
    {
        "question": "How to perform a calf raise?",
        "ground_truth": "Stand upright, push through the balls of your feet to raise your heels off the ground, then slowly lower back down.",
        "domain": "exercise",
    },
    {
        "question": "What equipment is needed for a kettlebell swing?",
        "ground_truth": "A kettlebell, focusing on explosive hip extension to swing the weight.",
        "domain": "exercise",
    },
    {
        "question": "Are sit-ups or crunches better for the core?",
        "ground_truth": "Both work the core, but crunches isolate the upper abdominals more effectively while minimizing strain on the lower back and hip flexors compared to full sit-ups.",
        "domain": "exercise",
    },
    {
        "question": "What is the primary function of the core muscles?",
        "ground_truth": "To stabilize the spine, pelvis, and kinetic chain during movements.",
        "domain": "exercise",
    },
    {
        "question": "What is a superset?",
        "ground_truth": "Performing two different exercises back-to-back with little or no rest in between.",
        "domain": "exercise",
    },
    {
        "question": "What is active recovery?",
        "ground_truth": "Low-intensity exercise performed on rest days to promote blood flow and muscle recovery without causing fatigue.",
        "domain": "exercise",
    },
    {
        "question": "What are plyometrics?",
        "ground_truth": "Explosive exercises like jump squats or box jumps designed to increase speed, power, and quickness.",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a farmer's walk?",
        "ground_truth": "Hold heavy weights in each hand and walk forward with a straight back, braced core, and controlled steps.",
        "domain": "exercise",
    },
    {
        "question": "What is the Valsalva maneuver during lifting?",
        "ground_truth": "Holding your breath against a closed glottis while straining, creating internal pressure to stabilize the spine during heavy lifts.",
        "domain": "exercise",
    },
    {
        "question": "What's the difference between static and dynamic stretching?",
        "ground_truth": "Static stretching holds a muscle in an elongated position, while dynamic stretching uses movement to gently stretch muscles; dynamic is better before workouts.",
        "domain": "exercise",
    },
    {
        "question": "What is a 1RM?",
        "ground_truth": "One Repetition Maximum, the maximum amount of weight a person can lift for one repetition of an exercise.",
        "domain": "exercise",
    },
    {
        "question": "What does eccentric contraction mean?",
        "ground_truth": "The lengthening phase of a muscle contraction, such as lowering the weight during a bicep curl.",
        "domain": "exercise",
    },
    {
        "question": "What is concentric contraction?",
        "ground_truth": "The shortening phase of a muscle contraction, such as lifting the weight during a bicep curl.",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a Russian twist?",
        "ground_truth": "Sit on the floor, lean back slightly with legs lifted, and rotate your torso side to side, optionally holding a weight.",
        "domain": "exercise",
    },
    {
        "question": "What muscle does the seated leg extension primarily target?",
        "ground_truth": "The quadriceps on the front of the thigh.",
        "domain": "exercise",
    },
    {
        "question": "What is a drop set?",
        "ground_truth": "A technique where you perform an exercise to failure, drop the weight, and immediately continue for more reps.",
        "domain": "exercise",
    },
    {
        "question": "What are the benefits of jumping rope?",
        "ground_truth": "It improves cardiovascular endurance, coordination, agility, and burns a high amount of calories.",
        "domain": "exercise",
    },
    {
        "question": "What is a clean and jerk?",
        "ground_truth": "An Olympic weightlifting movement where the barbell is lifted from the floor to the shoulders (clean), then pushed overhead (jerk).",
        "domain": "exercise",
    },
    {
        "question": "What are resistance bands used for?",
        "ground_truth": "They provide variable resistance for strength training, mobility work, and physical rehabilitation.",
        "domain": "exercise",
    },
    {
        "question": "How do you engage your lats during a deadlift?",
        "ground_truth": "By pulling your shoulders back and down, as if trying to squeeze an orange in your armpit.",
        "domain": "exercise",
    },
    {
        "question": "What is foam rolling?",
        "ground_truth": "A form of self-myofascial release used to relieve muscle tightness, soreness, and improve joint range of motion.",
        "domain": "exercise",
    },
    {
        "question": "What is the overhead press?",
        "ground_truth": "A weight training exercise in which a barbell or dumbbells are pressed straight upwards from the shoulders until the arms are locked out.",
        "domain": "exercise",
    },
    {
        "question": "What does a glute bridge target?",
        "ground_truth": "The gluteus maximus (buttocks) and the hamstrings.",
        "domain": "exercise",
    },
    {
        "question": "How many days a week should a beginner strength train?",
        "ground_truth": "Generally 2 to 3 days per week of full-body training is recommended for beginners.",
        "domain": "exercise",
    },
    {
        "question": "What is the benefit of unilateral exercises?",
        "ground_truth": "They work one side of the body at a time, helping to identify and correct muscular imbalances.",
        "domain": "exercise",
    },
    {
        "question": "What is a hack squat?",
        "ground_truth": "A squat variant typically performed on a machine that supports the back, emphasizing load on the quadriceps.",
        "domain": "exercise",
    },
    {
        "question": "What is cross-training?",
        "ground_truth": "Engaging in various different types of exercise (like running, swimming, and weightlifting) to improve overall performance and prevent overuse injuries.",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a kettlebell goblet squat?",
        "ground_truth": "Hold a kettlebell at chest height, keep your back straight, and lower your hips until your thighs are parallel to the floor, then stand back up.",
        "domain": "exercise",
    },
    {
        "question": "What muscles are targeted by the lat pulldown?",
        "ground_truth": "The latissimus dorsi, biceps, and rear deltoids.",
        "domain": "exercise",
    },
    {
        "question": "What is the primary benefit of a cool-down after exercising?",
        "ground_truth": "It helps gradually lower your heart rate and prevents blood from pooling in your extremities.",
        "domain": "exercise",
    },
    {
        "question": "What equipment do you need for a triceps rope pushdown?",
        "ground_truth": "A cable machine and a rope attachment.",
        "domain": "exercise",
    },
    {
        "question": "What is the difference between a pronated and supinated grip?",
        "ground_truth": "A pronated grip is palms facing down or away from you, and a supinated grip is palms facing up or towards you.",
        "domain": "exercise",
    },
    {
        "question": "What muscles does a Romanian deadlift primarily work?",
        "ground_truth": "The hamstrings, glutes, and lower back.",
        "domain": "exercise",
    },
    {
        "question": "How do you do a push-up with proper form?",
        "ground_truth": "Keep your body in a straight line, hands slightly wider than shoulder-width, lower your chest to the floor, and push back up.",
        "domain": "exercise",
    },
    {
        "question": "What is the main function of the gluteus maximus?",
        "ground_truth": "It is the primary extensor muscle of the hip.",
        "domain": "exercise",
    },
    {
        "question": "What makes an exercise an isolation movement?",
        "ground_truth": "It targets primarily one muscle group and involves movement at only one joint.",
        "domain": "exercise",
    },
    {
        "question": "Why is core stability important for heavy lifting?",
        "ground_truth": "It protects the spine and improves the transfer of force between the lower and upper body.",
        "domain": "exercise",
    },
    {
        "question": "How do you do a Bulgarian split squat?",
        "ground_truth": "Place your back foot on an elevated bench, keep your chest up, and lower your hips until your front thigh is parallel to the ground.",
        "domain": "exercise",
    },
    {
        "question": "What is the difference between free weights and machines?",
        "ground_truth": "Free weights require more stabilization and use a natural range of motion, while machines guide the movement and isolate muscles better.",
        "domain": "exercise",
    },
    {
        "question": "What does RPE stand for in training?",
        "ground_truth": "Rate of Perceived Exertion, used to measure the intensity of your exercise on a scale (usually 1-10).",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a medicine ball slam?",
        "ground_truth": "Hold a medicine ball overhead and forcefully slam it into the ground, engaging the core and lats.",
        "domain": "exercise",
    },
    {
        "question": "What is a superset?",
        "ground_truth": "Performing two exercises back to back with no rest in between.",
        "domain": "exercise",
    },
    {
        "question": "What are fast-twitch muscle fibers?",
        "ground_truth": "Muscle fibers that generate short, explosive bursts of energy but fatigue quickly.",
        "domain": "exercise",
    },
    {
        "question": "What is the purpose of a spotter during weightlifting?",
        "ground_truth": "To assist the lifter in case they fail a repetition, ensuring safety during heavy lifts.",
        "domain": "exercise",
    },
    {
        "question": "How do you properly perform a barbell hip thrust?",
        "ground_truth": "Rest your upper back on a bench, place a barbed across your hips, and thrust your hips upward, squeezing the glutes.",
        "domain": "exercise",
    },
    {
        "question": "What does AMRAP stand for?",
        "ground_truth": "As Many Reps (or Rounds) As Possible in a given timeframe.",
        "domain": "exercise",
    },
    {
        "question": "What muscles do dips primarily target?",
        "ground_truth": "The triceps, anterior deltoids, and the lower portion of the pectoralis major.",
        "domain": "exercise",
    },
    {
        "question": "Why use lifting belts?",
        "ground_truth": "They help increase intra-abdominal pressure to stabilize the spine during heavy compound lifts.",
        "domain": "exercise",
    },
    {
        "question": "What is hypertrophy training?",
        "ground_truth": "Training specifically designed to increase the size of muscle fibers.",
        "domain": "exercise",
    },
    {
        "question": "How do you do a side plank?",
        "ground_truth": "Lie on your side, prop yourself up on one forearm, lift your hips so your body forms a straight line, and hold.",
        "domain": "exercise",
    },
    {
        "question": "What is a drop set?",
        "ground_truth": "Performing an exercise to failure, then immediately dropping the weight and continuing for more reps.",
        "domain": "exercise",
    },
    {
        "question": "What are the benefits of swimming for exercise?",
        "ground_truth": "It provides a full-body, low-impact cardiovascular workout that also builds muscular endurance.",
        "domain": "exercise",
    },
    {
        "question": "How do you correctly breathe during weightlifting?",
        "ground_truth": "Inhale during the eccentric (lowering) phase and exhale during the concentric (lifting) phase.",
        "domain": "exercise",
    },
    {
        "question": "What is cross-training?",
        "ground_truth": "Engaging in various sports or exercises to improve overall performance and prevent injury.",
        "domain": "exercise",
    },
    {
        "question": "What is a calorie surplus?",
        "ground_truth": "Consuming more calories than you burn, which is necessary for building muscle mass.",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a reverse lunge?",
        "ground_truth": "Take a step backward, bend both knees to 90 degrees, and push off the back foot to return to the starting position.",
        "domain": "exercise",
    },
    {
        "question": "What does a seated cable row target?",
        "ground_truth": "The muscles of the middle back, primarily the rhomboids, trapezius, and latissimus dorsi.",
        "domain": "exercise",
    },
    {
        "question": "What are resistance bands?",
        "ground_truth": "Elastic bands used for strength training and physical therapy that provide variable tension.",
        "domain": "exercise",
    },
    {
        "question": "What is the difference between unilateral and bilateral exercises?",
        "ground_truth": "Unilateral exercises use one limb at a time (e.g., lunges), while bilateral use both limbs together (e.g., squats).",
        "domain": "exercise",
    },
    {
        "question": "How do you do a proper wall sit?",
        "ground_truth": "Lean your back against a wall, slide down until your knees are at a 90-degree angle, and hold the position.",
        "domain": "exercise",
    },
    {
        "question": "What muscles do mountain climbers work?",
        "ground_truth": "The core, shoulders, triceps, and hip flexors, while also raising the heart rate.",
        "domain": "exercise",
    },
    {
        "question": "What is a deload week?",
        "ground_truth": "A planned reduction in training volume or intensity to allow the body to recover and prevent overtraining.",
        "domain": "exercise",
    },
    {
        "question": "Why is form more important than weight lifted?",
        "ground_truth": "Proper form ensures the correct muscles are targeted and drastically reduces the risk of injury.",
        "domain": "exercise",
    },
    {
        "question": "How do you do a box jump?",
        "ground_truth": "Stand in front of a plyometric box, squat slightly, swing your arms, and jump onto the box, landing softly.",
        "domain": "exercise",
    },
    {
        "question": "What does EMOM stand for?",
        "ground_truth": "Every Minute on the Minute, performing a specific task at the start of every minute.",
        "domain": "exercise",
    },
    {
        "question": "What is functional training?",
        "ground_truth": "Exercises that simulate everyday movements to improve strength, balance, and coordination for daily life.",
        "domain": "exercise",
    },
    {
        "question": "How do you properly perform a bicep curl?",
        "ground_truth": "Hold a weight with an underhand grip, keep elbows pinned to your sides, and curl the weight up towards your shoulders.",
        "domain": "exercise",
    },
    {
        "question": "What does a stationary bike workout look like?",
        "ground_truth": "Pedaling on a stationary machine, often incorporating varied resistance and speed intervals for cardio.",
        "domain": "exercise",
    },
    {
        "question": "What is periodization in fitness?",
        "ground_truth": "The systematic planning of athletic training by dividing it into specific cycles to peak at the right time.",
        "domain": "exercise",
    },
    {
        "question": "How do you use a foam roller on your IT band?",
        "ground_truth": "Lie on your side with the roller under your outer thigh, place your top foot in front, and roll from hip to knee.",
        "domain": "exercise",
    },
    {
        "question": "What is the difference between muscular strength and muscular endurance?",
        "ground_truth": "Strength is the maximum amount of force a muscle can produce, while endurance is its ability to perform repeated contractions over time.",
        "domain": "exercise",
    },
    {
        "question": "How do you perform a classic jumping jack?",
        "ground_truth": "Jump up, spreading your legs wide and bringing your hands together overhead, then jump back to the starting position.",
        "domain": "exercise",
    },
    {
        "question": "What do calisthenics exercises rely on?",
        "ground_truth": "Body weight for resistance, requiring minimal to no equipment (e.g., push-ups, pull-ups).",
        "domain": "exercise",
    },
    {
        "question": "How do you do a skull crusher?",
        "ground_truth": "Lie on a bench, hold an EZ bar straight above your chest, bend your elbows to lower the bar to your forehead, and extend back up.",
        "domain": "exercise",
    },
    {
        "question": "What is the primary benefit of yoga?",
        "ground_truth": "It improves flexibility, balance, and mind-body connection through controlled breathing and poses.",
        "domain": "exercise",
    },
    {
        "question": "How do you execute a barbell overhead press?",
        "ground_truth": "Stand with a barbell at collarbone height, brace your core, and press it directly overhead until arms are locked.",
        "domain": "exercise",
    },
    {
        "question": "What are the benefits of using a rowing machine?",
        "ground_truth": "It provides a low-impact, full-body cardiovascular and strength workout simultaneously.",
        "domain": "exercise",
    },
]


def load_eval_dataset(pipeline=None, use_rag_contexts=True):
    """
    Build a RAGAS-compatible dataset from the curated Q&A pairs.

    Args:
        pipeline: RAGLLMPipeline instance (required if use_rag_contexts=True)
        use_rag_contexts: If True, retrieve real contexts from ChromaDB per question.
                         If False, use a placeholder context (faster, for testing).

    Returns:
        dict with lists: questions, answers, contexts, ground_truths, domains
    """
    from datasets import Dataset

    questions    = []
    answers      = []
    contexts     = []
    ground_truths = []
    domains_list = []

    print(f"\n{'='*60}")
    print("Building Evaluation Dataset")
    print(f"{'='*60}")
    print(f"Total questions: {len(EVAL_QUESTIONS)}")

    for i, item in enumerate(EVAL_QUESTIONS, 1):
        q           = item["question"]
        gt          = item["ground_truth"]
        domain      = item.get("domain")
        domain_label = domain if domain else "all"

        print(f"  [{i:02d}/{len(EVAL_QUESTIONS)}] {domain_label}: {q[:60]}...")

        if use_rag_contexts and pipeline is not None:
            # Retrieve real context from ChromaDB
            context_str = pipeline.retrieval_engine.get_context_for_llm(
                q, domain=domain, n_results=3
            )
            # Generate the actual model answer using the full pipeline
            result = pipeline.process_query(q, domain=domain, n_context_results=3)
            answer = result["english_response"]  # Always use English for evaluation
        else:
            # Fallback: placeholder for quick dataset structure testing
            context_str = f"[Context for: {q}]"
            answer      = "[Answer placeholder — run with pipeline for real answers]"

        questions.append(q)
        answers.append(answer)
        contexts.append([context_str])  # RAGAS expects a list of context strings
        ground_truths.append(gt)
        domains_list.append(domain_label)

    print(f"\n✓ Dataset built: {len(questions)} samples")

    # Wrap in HuggingFace Dataset (RAGAS native format)
    hf_dataset = Dataset.from_dict({
        "question":     questions,
        "answer":       answers,
        "contexts":     contexts,
        "ground_truth": ground_truths,
        "domain":       domains_list,
    })

    return hf_dataset, domains_list


if __name__ == "__main__":
    print("Eval dataset structure test (no pipeline — placeholder mode):")
    ds, _ = load_eval_dataset(pipeline=None, use_rag_contexts=False)
    print(ds)
    print(f"\nColumns: {ds.column_names}")
    print(f"Rows:    {len(ds)}")
    print("\nSample row:")
    print(f"  Q:  {ds[0]['question']}")
    print(f"  GT: {ds[0]['ground_truth'][:80]}...")
