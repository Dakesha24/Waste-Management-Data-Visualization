from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib

# Use 'Agg' backend for Matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# Load data
data_file = os.path.join('data', 'Data_Timbulan_Sampah_SIPSN_KLHK.xlsx')

# Read the Excel file with the correct header row
df = pd.read_excel(data_file, header=1)

# Strip any leading/trailing whitespace from the column names
df.columns = df.columns.str.strip()

# Convert the column to float if it's not already
df['Timbulan Sampah Tahunan(ton)'] = df['Timbulan Sampah Tahunan(ton)'].astype(float)

# Group by province and year
annual_waste = df.groupby(['Tahun', 'Provinsi'])['Timbulan Sampah Tahunan(ton)'].sum().reset_index()
average_waste = annual_waste.groupby('Provinsi')['Timbulan Sampah Tahunan(ton)'].mean().reset_index()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/total_annual_waste')
def total_annual_waste():
    # Plotting
    plt.figure(figsize=(18, 10))
    for province in annual_waste['Provinsi'].unique():
        province_data = annual_waste[annual_waste['Provinsi'] == province]
        plt.plot(province_data['Tahun'], province_data['Timbulan Sampah Tahunan(ton)'], label=province)
    plt.xlabel('Year')
    plt.ylabel('Total Annual Waste (tons)')
    plt.title('Total Annual Waste Generation by Province')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig('static/total_annual_waste.png')
    plt.close()

    return render_template('graphs.html', graph='total_annual_waste.png')

@app.route('/average_annual_waste')
def average_annual_waste():
    # Categorization
    conditions = [
        (average_waste['Timbulan Sampah Tahunan(ton)'] <= 100000),
        (average_waste['Timbulan Sampah Tahunan(ton)'] > 100000) & (average_waste['Timbulan Sampah Tahunan(ton)'] <= 700000),
        (average_waste['Timbulan Sampah Tahunan(ton)'] > 700000)
    ]
    categories = ['GREEN', 'ORANGE', 'RED']
    average_waste['Category'] = pd.cut(average_waste['Timbulan Sampah Tahunan(ton)'], bins=[0, 100000, 700000, float('inf')], labels=categories, right=False)

    # Plotting
    plt.figure(figsize=(15, 8))  # Set larger figure size
    colors = {'GREEN': 'green', 'ORANGE': 'orange', 'RED': 'red'}
    for category in categories:
        category_data = average_waste[average_waste['Category'] == category]
        plt.bar(category_data['Provinsi'], category_data['Timbulan Sampah Tahunan(ton)'], label=category, color=colors.get(category, 'blue'))
    plt.xlabel('Province')
    plt.ylabel('Average Annual Waste (tons)')
    plt.title('Average Annual Waste Generation by Province')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend position
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('static/average_annual_waste.png')
    plt.close()

    return render_template('graphs.html', graph='average_annual_waste.png')

if __name__ == '__main__':
    app.run(debug=True)
