import json

new_questions = [
    {"question": "What primary muscles are targeted by the bench press?", "ground_truth": "The pectoralis major (chest), anterior deltoids (front shoulders), and triceps.", "domain": "exercise"},
    {"question": "How do you perform a proper barbell squat?", "ground_truth": "Keep chest up, back straight, bend at the knees and hips, lowering your body until thighs are parallel to the floor, then push back up.", "domain": "exercise"},
    {"question": "What is the difference between a hammer curl and a standard bicep curl?", "ground_truth": "A hammer curl uses a neutral grip (palms facing each other), focusing more on the brachialis and brachioradialis, while a standard curl uses an underhand grip.", "domain": "exercise"},
    {"question": "What are the benefits of cardiovascular exercise?", "ground_truth": "Improves heart health, increases lung capacity, aids in weight loss, and reduces stress.", "domain": "exercise"},
    {"question": "Which muscles does a plank strengthen?", "ground_truth": "The transversus abdominis, rectus abdominis, obliques, and shoulders.", "domain": "exercise"},
    {"question": "What is a deadlift?", "ground_truth": "A compound weight training exercise in which a loaded barbell is lifted off the ground to the level of the hips, then lowered.", "domain": "exercise"},
    {"question": "How do you do a pull-up?", "ground_truth": "Hang from a pull-up bar with an overhand grip, pull your body up until your chin clears the bar, and lower yourself back down with control.", "domain": "exercise"},
    {"question": "What is HIIT?", "ground_truth": "High-Intensity Interval Training involves short bursts of intense exercise alternated with low-intensity recovery periods.", "domain": "exercise"},
    {"question": "How often should you rest between strength training workouts for the same muscle group?", "ground_truth": "Generally 48 hours is recommended to allow for adequate muscle recovery.", "domain": "exercise"},
    {"question": "What muscles does a lunge work?", "ground_truth": "Quadriceps, hamstrings, glutes, and calves.", "domain": "exercise"},
    {"question": "What is the purpose of a warm-up before exercising?", "ground_truth": "To gradually increase heart rate, improve blood flow to muscles, and reduce the risk of injury.", "domain": "exercise"},
    {"question": "What is progressive overload?", "ground_truth": "Gradually increasing the weight, frequency, or number of repetitions in your strength training routine to continuously challenge the muscles.", "domain": "exercise"},
    {"question": "How many minutes of moderate aerobic exercise are recommended per week?", "ground_truth": "At least 150 minutes per week, according to major health guidelines.", "domain": "exercise"},
    {"question": "What is a compound exercise?", "ground_truth": "An exercise that works multiple muscle groups and joints at the same time, such as squats or deadlifts.", "domain": "exercise"},
    {"question": "What is an isolation exercise?", "ground_truth": "An exercise that targets a single muscle group and involves only one joint, such as a bicep curl.", "domain": "exercise"},
    {"question": "What is the difference between aerobic and anaerobic exercise?", "ground_truth": "Aerobic exercise requires steady oxygen (like running), while anaerobic involves quick bursts of energy without relying on oxygen (like sprinting or heavy lifting).", "domain": "exercise"},
    {"question": "How do you do a burpee?", "ground_truth": "Start standing, drop into a squat, kick your feet back to a plank, do a push-up, jump your feet back to a squat, and jump up.", "domain": "exercise"},
    {"question": "What muscles are worked during a Romanian Deadlift (RDL)?", "ground_truth": "Hamstrings, glutes, and lower back erectors.", "domain": "exercise"},
    {"question": "What is DOMS?", "ground_truth": "Delayed Onset Muscle Soreness is the muscle pain and stiffness felt 24 to 72 hours after unaccustomed or strenuous exercise.", "domain": "exercise"},
    {"question": "Why is stretching important after a workout?", "ground_truth": "It helps improve flexibility, reduces muscle tension, and brings your heart rate down gradually.", "domain": "exercise"},
    {"question": "What is the Romanian twist?", "ground_truth": "Likely referring to the Russian twist, a core exercise that involves rotating the torso from side to side to engage the obliques.", "domain": "exercise"},
    {"question": "What makes a Bulgarian split squat different from a regular lunge?", "ground_truth": "The rear foot is elevated on a bench or block, which increases the range of motion and places more load on the front leg.", "domain": "exercise"},
    {"question": "What does a lat pulldown target?", "ground_truth": "The latissimus dorsi muscles in the middle back, as well as the biceps and rear deltoids.", "domain": "exercise"},
    {"question": "How to perform a calf raise?", "ground_truth": "Stand upright, push through the balls of your feet to raise your heels off the ground, then slowly lower back down.", "domain": "exercise"},
    {"question": "What equipment is needed for a kettlebell swing?", "ground_truth": "A kettlebell, focusing on explosive hip extension to swing the weight.", "domain": "exercise"},
    {"question": "Are sit-ups or crunches better for the core?", "ground_truth": "Both work the core, but crunches isolate the upper abdominals more effectively while minimizing strain on the lower back and hip flexors compared to full sit-ups.", "domain": "exercise"},
    {"question": "What is the primary function of the core muscles?", "ground_truth": "To stabilize the spine, pelvis, and kinetic chain during movements.", "domain": "exercise"},
    {"question": "What is a superset?", "ground_truth": "Performing two different exercises back-to-back with little or no rest in between.", "domain": "exercise"},
    {"question": "What is active recovery?", "ground_truth": "Low-intensity exercise performed on rest days to promote blood flow and muscle recovery without causing fatigue.", "domain": "exercise"},
    {"question": "What are plyometrics?", "ground_truth": "Explosive exercises like jump squats or box jumps designed to increase speed, power, and quickness.", "domain": "exercise"},
    {"question": "How do you perform a farmer's walk?", "ground_truth": "Hold heavy weights in each hand and walk forward with a straight back, braced core, and controlled steps.", "domain": "exercise"},
    {"question": "What is the Valsalva maneuver during lifting?", "ground_truth": "Holding your breath against a closed glottis while straining, creating internal pressure to stabilize the spine during heavy lifts.", "domain": "exercise"},
    {"question": "What's the difference between static and dynamic stretching?", "ground_truth": "Static stretching holds a muscle in an elongated position, while dynamic stretching uses movement to gently stretch muscles; dynamic is better before workouts.", "domain": "exercise"},
    {"question": "What is a 1RM?", "ground_truth": "One Repetition Maximum, the maximum amount of weight a person can lift for one repetition of an exercise.", "domain": "exercise"},
    {"question": "What does eccentric contraction mean?", "ground_truth": "The lengthening phase of a muscle contraction, such as lowering the weight during a bicep curl.", "domain": "exercise"},
    {"question": "What is concentric contraction?", "ground_truth": "The shortening phase of a muscle contraction, such as lifting the weight during a bicep curl.", "domain": "exercise"},
    {"question": "How do you perform a Russian twist?", "ground_truth": "Sit on the floor, lean back slightly with legs lifted, and rotate your torso side to side, optionally holding a weight.", "domain": "exercise"},
    {"question": "What muscle does the seated leg extension primarily target?", "ground_truth": "The quadriceps on the front of the thigh.", "domain": "exercise"},
    {"question": "What is a drop set?", "ground_truth": "A technique where you perform an exercise to failure, drop the weight, and immediately continue for more reps.", "domain": "exercise"},
    {"question": "What are the benefits of jumping rope?", "ground_truth": "It improves cardiovascular endurance, coordination, agility, and burns a high amount of calories.", "domain": "exercise"},
    {"question": "What is a clean and jerk?", "ground_truth": "An Olympic weightlifting movement where the barbell is lifted from the floor to the shoulders (clean), then pushed overhead (jerk).", "domain": "exercise"},
    {"question": "What are resistance bands used for?", "ground_truth": "They provide variable resistance for strength training, mobility work, and physical rehabilitation.", "domain": "exercise"},
    {"question": "How do you engage your lats during a deadlift?", "ground_truth": "By pulling your shoulders back and down, as if trying to squeeze an orange in your armpit.", "domain": "exercise"},
    {"question": "What is foam rolling?", "ground_truth": "A form of self-myofascial release used to relieve muscle tightness, soreness, and improve joint range of motion.", "domain": "exercise"},
    {"question": "What is the overhead press?", "ground_truth": "A weight training exercise in which a barbell or dumbbells are pressed straight upwards from the shoulders until the arms are locked out.", "domain": "exercise"},
    {"question": "What does a glute bridge target?", "ground_truth": "The gluteus maximus (buttocks) and the hamstrings.", "domain": "exercise"},
    {"question": "How many days a week should a beginner strength train?", "ground_truth": "Generally 2 to 3 days per week of full-body training is recommended for beginners.", "domain": "exercise"},
    {"question": "What is the benefit of unilateral exercises?", "ground_truth": "They work one side of the body at a time, helping to identify and correct muscular imbalances.", "domain": "exercise"},
    {"question": "What is a hack squat?", "ground_truth": "A squat variant typically performed on a machine that supports the back, emphasizing load on the quadriceps.", "domain": "exercise"},
    {"question": "What is cross-training?", "ground_truth": "Engaging in various different types of exercise (like running, swimming, and weightlifting) to improve overall performance and prevent overuse injuries.", "domain": "exercise"}
]

with open(r'c:\Users\Mohamed Metwaly\Downloads\Final Draft\evaluation\eval_dataset.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find the end of EVAL_QUESTIONS = [ ... ]
# The array ends with:
#     },
# ]

target = '''    {
        "question": "How do you tell if an egg is fresh?",
        "ground_truth": "Place it in water; fresh eggs sink and lay flat, while old eggs float.",
        "domain": "nutrition",
    },
]'''

replacement_items = ""
for item in new_questions:
    replacement_items += f'''    {{
        "question": "{item['question']}",
        "ground_truth": "{item['ground_truth']}",
        "domain": "{item['domain']}",
    }},
'''

replacement = f'''    {{
        "question": "How do you tell if an egg is fresh?",
        "ground_truth": "Place it in water; fresh eggs sink and lay flat, while old eggs float.",
        "domain": "nutrition",
    }},
{replacement_items}]'''

new_content = content.replace(target, replacement)

with open(r'c:\Users\Mohamed Metwaly\Downloads\Final Draft\evaluation\eval_dataset.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done inserting 50 questions!")
