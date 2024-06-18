import pandas as pd
from pandasai.skills import skill


@skill
def plot_daily_run_rate_leads(dataframe: pd.DataFrame, save_charts_path: str):
    """
    Plots the leads with date on the x-axis and leads on the y-axis using Matplotlib.
    The actual values (date < current_date) are plotted in blue and the expected values
    (date >= current_date) are plotted in red.

    Args:
        dataframe (pd.DataFrame): DataFrame containing 'date' and 'leads' columns.
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    from datetime import datetime

    # Convert 'date' column to datetime format
    dataframe['date'] = pd.to_datetime(dataframe['date'])

    # Get current date in datetime64[ns] format
    current_date = pd.to_datetime(datetime.now().date())

    # Split the data into actual and expected
    actual_data = dataframe[dataframe['date'] < current_date]
    expected_data = dataframe[dataframe['date'] >= current_date]

    # Plotting the data
    plt.figure(figsize=(12, 6))

    # Plot actual data
    plt.plot(actual_data['date'], actual_data['leads'], color='blue', label='Actual')

    # Plot expected data
    plt.plot(expected_data['date'], expected_data['leads'], color='red', label='Expected')

    # Adding annotations
    for idx, row in actual_data.iterrows():
        plt.annotate(f"{row['leads']:.0f}", (row['date'], row['leads']), textcoords="offset points", xytext=(0, 10),
                     ha='center')
    for idx, row in expected_data.iterrows():
        plt.annotate(f"{row['leads']:.0f}", (row['date'], row['leads']), textcoords="offset points", xytext=(0, 10),
                     ha='center')

    # Customizing the plot
    plt.xlabel("Date")
    plt.ylabel("Leads")
    plt.title("Actual vs Expected Leads")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as an image
    plt.savefig(save_charts_path)
    fig = plt.gcf()

    return fig