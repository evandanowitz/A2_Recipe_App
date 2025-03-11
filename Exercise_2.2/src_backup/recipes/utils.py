# This file is to implement charting functions

"""
Utility functions for chart generation in BiteBase.
Handles data visualization using Matplotlib and processes chart images.
"""

from io import BytesIO
import base64
import matplotlib.pyplot as plt
import pandas as pd # pandas for data manipulation

def get_graph():
  """
  get_graph() takes care of low-level image-handling details for charts.
  get_graph() must be called by another function--called "get_chart()".
  Converts Matplotlib chart to a base64-encoded string.
  Returns: str: Base64 encoded image.
  """
  buffer = BytesIO() # Create a BytesIO buffer for the image
  plt.savefig(buffer, format='png') # Save the plot as a PNG image in buffer
  buffer.seek(0) # Move cursor to the start of the buffer
  image_png = buffer.getvalue() # Retrieve image data from buffer
  graph = base64.b64encode(image_png).decode('utf-8') # Convert to base64 string
  buffer.close() # Free memory by closing the buffer
  return graph # Return the base64-encdoed image

def get_chart(chart_type, data):
  """
  Generates a chart based on the selected type and data.
  Args:
  - chart_type (str): The type of chart ("#1" - Bar, "#2" - Pie, "#3" - Line).
  - data (DataFrame): Recipe data.
  Returns:
  - str or None: Base64-encoded chart image or None if invalid chart type.
  """
  plt.switch_backend('AGG') # Use AGG backend (no GUI)
  fig = plt.figure(figsize = (8, 5)) # Set chart figure size

  # Bar Chart - Recipes by Difficulty
  if chart_type == '#1':
    difficulty_order = ['Easy', 'Medium', 'Intermediate', 'Hard']
    difficulty_counts = data['difficulty'].value_counts().reindex(difficulty_order, fill_value=0)
    
    plt.bar(
      difficulty_counts.index, 
      difficulty_counts.values, 
      color = ['#2a9d8f', '#f4a261', '#e76f51', '#264653']
    )
    plt.xlabel('Difficulty Level', fontsize=16)
    plt.ylabel('Number of Recipes', fontsize=16)
    plt.title('Recipes by Difficulty Level', fontsize=20)
  
  # Pie Chart - Cooking Time Distribution
  elif chart_type == '#2':
    bins = [0, 10, 30, 60, float('inf')] # Define time range bins
    labels = ['0-10 mins', '11-30 mins', '31-60 mins', '60+ mins']
    data['time_category'] = pd.cut(data['cooking_time'], bins=bins, labels=labels, right=False)
    time_distribution = data['time_category'].value_counts()
    colors = ['#2a9d8f', '#f4a261', '#e76f51', '#264653']

    def count_labels(pct):
      """ Converts percentage to count for pie chart labels. """
      total = sum(time_distribution)
      count = int(pct * total / 100)
      return f'{count}\nrecipes' if count > 0 else ''

    plt.pie(
      time_distribution, 
      labels = labels,
      colors = colors,
      autopct = count_labels,
      labeldistance = 1.1,
      startangle = 140,
      textprops = {'fontsize': 12}
    )
    plt.title('Cooking Time Distribution', fontsize=20)

  # Line Chart - Most Common Ingredients
  elif chart_type == '#3':
    ingredient_counts = (
      data['ingredients']
      .str.split(',')
      .explode()
      .str.strip()
      .value_counts()
      .head(5)
    )

    plt.plot(ingredient_counts.index, ingredient_counts.values, marker = 'o', linestyle = '-')
    plt.xlabel('Ingredients (Top 5)', fontsize = 16)
    plt.ylabel('# of Recipes Containing Ingredient', fontsize = 16)
    plt.title('Most Common Ingredients in Recipes', fontsize = 20)

    plt.xticks(rotation = 20, ha = 'right', fontsize = 14)
    plt.yticks(fontsize = 14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

  else:
    return None # Return None if an invalid chart type is provided

  plt.tight_layout() # Prevent overlap in chart layout
  return get_graph() # Return the generated chart as a base64 string