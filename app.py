# Step 1: Import the necessary libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 2: Load your dataset
# Make sure the CSV file is in the same directory as your script/notebook,
# or provide the full path to the file.
file_path = 'generated_aqi_data.csv'
df = pd.read_csv(file_path)

# Optional: Drop the 'Date' and 'City' columns for the correlation calculation,
# as .corr() only works on numerical data.
df_numeric = df.drop(columns=['Date', 'City'])

# Step 3: Calculate the correlation matrix
# The .corr() method calculates the Pearson correlation coefficient between all pairs of columns.
correlation_matrix = df_numeric.corr()

# Step 4: Generate the heatmap
# We'll set up the plot size first for better readability.
plt.figure(figsize=(12, 10))

# The core command to create the heatmap
sns.heatmap(
    correlation_matrix, 
    annot=True,          # This displays the correlation values on the heatmap
    fmt='.2g',           # Formats the numbers to be cleaner (e.g., 0.97 instead of 0.970000)
    cmap='rocket_r'      # Sets the color map. '_r' reverses it to match your example (bright = high)
)

# Add a title for clarity
plt.title('Correlation Heatmap of AQI Data', fontsize=16)

# Display the plot
plt.show()