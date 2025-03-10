# This file is to implement charting functions

from io import BytesIO
import base64
import matplotlib.pyplot as plt
import pandas as pd                 # Import pandas for data manipulation

# The get_graph() function will take care of the low-level image-handling details for charts.
# The get_graph() function must be called by another function ( will be called "get_chart()" ).
def get_graph():
  buffer = BytesIO() # Create a BytesIO buffer for the image
  plt.savefig(buffer, format='png') # Create a plot with a bytesIO object as a file-like object. Set format to png
  buffer.seek(0) # Set cursor to the beginning of the stream
  image_png = buffer.getvalue() # Retrieve the content of the file
  graph = base64.b64encode(image_png) # Encode the bytes-like object
  graph = graph.decode('utf-8') # Decode to get the string as output
  buffer.close() # Free up the memory of buffer
  return graph # Return the image / graph

# Implements the logic to prepare chart based on user input. Calls get_graph() to generate chart at file/byte level.
def get_chart(chart_type, data):
  plt.switch_backend('AGG') # Switch plot backend to AGG (Anti-Grain Geometry) – to write to file. Preferred way to write PNG files.
  fig = plt.figure(figsize = (8, 5)) # Specify figure size (creates a blank figure)

  # Bar Chart – Recipes by Difficulty
  if chart_type == '#1':
    difficulty_order = ['Easy', 'Medium', 'Intermediate', 'Hard']
    difficulty_counts = data['difficulty'].value_counts().reindex(difficulty_order, fill_value=0) # Count number of recipes per difficulty level
    plt.bar(difficulty_counts.index, difficulty_counts.values, color = ['#2a9d8f', '#f4a261', '#e76f51', '#264653'])
    plt.xlabel('Difficulty Level', fontsize=16)
    plt.ylabel('Number of Recipes', fontsize=16)
    plt.title('Recipes by Difficulty Level', fontsize=20)

    difficulty_counts = data['difficulty'].value_counts()
    print('Difficulty Counts:\n', difficulty_counts)
  
  # Pie Chart – Cooking Time Distribution
  elif chart_type == '#2':
    bins = [0, 10, 30, 60, float('inf')]                                                          # Define cooking time ranges
    labels = ['0-10 mins', '11-30 mins', '31-60 mins', '60+ mins']                                # Labels for each range
    data['time_category'] = pd.cut(data['cooking_time'], bins=bins, labels=labels, right=False)   # Categorize each recipe into a time range
    time_distribution = data['time_category'].value_counts()                                      # Count number of recipes in each time range category
    colors = ['#2a9d8f', '#f4a261', '#e76f51', '#264653']                                         # Define colors for better readability

    def count_labels(pct):                              # Function to display actual count instead of percentage
      total = sum(time_distribution)                    # Get total number of recipes
      count = int(pct * total / 100)                    # Convert percentage to count
      return f'{count}\nrecipes' if count > 0 else ''   # Show count, but hide zero values

    # Create the Pie Chart
    plt.pie(time_distribution, 
      labels = labels,            # Keep time ranges outside
      colors = colors,            # Apply custom colors
      autopct = count_labels,     # Show recipe count inside each section
      labeldistance = 1.1,        # Distance of labels from center
      startangle = 140,           # Rotate chart for better visibility
      textprops = {'fontsize': 12}
    )
    plt.title('Cooking Time Distribution', fontsize=20)

  # Line Chart – Most Common Ingredients
  elif chart_type == '#3':
    ingredient_counts = (
      data['ingredients']
      .str.split(',')
      .explode()
      .str.strip()
      .value_counts()
      .head(5)
    )
  
    # Labels and Titles
    plt.plot(ingredient_counts.index, ingredient_counts.values, marker = 'o', linestyle = '-')
    plt.xlabel('Ingredients (Top 5)', fontsize = 16)
    plt.ylabel('# of Recipes Containing Ingredient', fontsize = 16)
    plt.title('Most Common Ingredients in Recipes', fontsize = 20)

    # Rotate X-axis labels for readability
    plt.xticks(rotation = 20, ha = 'right', fontsize = 14)    # X-axis ticks labels rotation and font size
    plt.yticks(fontsize = 14)                                 # Y-axis label ticks font size
    plt.grid(axis='y', linestyle='--', alpha=0.7)             # Add grid for better readability

  else:
    print('Unknown Chart Type')
    return None # Return None for an invalid chart type

  plt.tight_layout() # Prevents chart overlap
  return get_graph() # Renders the generated graph/chart to file