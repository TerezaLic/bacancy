import pandas as pd
import altair as alt
import streamlit as st


def process_raw_data(raw_dataframe, fields):
    pivot_column = fields.get('pivot_column')
    # raw_dataframe = pd.read_excel(inputfile, header=1)
    
    # Extract column names and filteration 
    # column_names = raw_dataframe.columns.tolist()
    # cleaned_column_names = [col.replace(" ", "") for col in column_names]  # Remove spaces from column names
    # raw_dataframe.columns = cleaned_column_names     # Assign the cleaned column names back to the DataFrame

    process_dataframe = raw_dataframe[["primary_datetime_dimension_value", "metric_value", "dimension_1_string_value"]]
    process_dataframe = process_dataframe.rename(
        columns={
            "primary_datetime_dimension_value": "invoice_date",
            "metric_value": "revenue",
            "dimension_1_string_value": "region"
        }
    )
    unique_regions = list(raw_dataframe['dimension_1_string_value'].sort_values().unique())
    response = {}
    
    if pivot_column:
        process_dataframe = process_dataframe.pivot(index='invoice_date', columns='region', values='revenue').reset_index()
        process_dataframe['total_revenue'] = process_dataframe['APAC'] + process_dataframe['Americas'] + process_dataframe['EMEA']
        response['pivot_unique'] = unique_regions
    
    
    response['df'] = process_dataframe
    # print('process_dataframe: ', process_dataframe)
    return response 


def line_chart(process_response, fields):
    df = process_response.get('df')
    # print('df: ', df)
    pivot_unique = process_response.get('pivot_unique')
    print('pivot_unique: ', pivot_unique)
    values_data = ['total_revenue']
    filtered_data = df.copy()

    if pivot_unique:
        # Ensure pivot_unique is a list
        # pivot_unique = list(pivot_unique)
        
        # Filter the data for all available data
        values_data = pivot_unique + ['total_revenue']

        # Melt the filtered data for Altair line chart
        melted_data = filtered_data.melt(id_vars=['invoice_date'], value_vars=values_data, var_name='region', value_name='revenue')
        print('melted_data: ', melted_data)

        # Line chart with Altair
        line_chart = alt.Chart(melted_data).mark_line().encode(
            x='invoice_date:T',
            y='revenue:Q',
            color='region:N'
        ).properties(
            height=400,
            title='Line Chart of Revenue Over Time by Region'
        ).interactive()
    else:
        # Line chart with only invoice_date and total_revenue
        line_chart = alt.Chart(filtered_data).mark_line().encode(
            x='invoice_date:T',
            y='revenue:Q'
        ).properties(
            height=400,
            title='Line Chart of Total Revenue Over Time'
        ).interactive()

    
    return line_chart

    
def combined_chart(process_response, fields):
    df = process_response.get('df')
    pivot_unique = process_response.get('pivot_unique')
    filtered_data = df.copy()
    if pivot_unique:
            # Ensure pivot_unique is a list
        pivot_unique = list(pivot_unique)

        # Sum the revenue for each region
        region_revenue = filtered_data[pivot_unique].sum().reset_index()
        region_revenue.columns = ['region', 'revenue']

        # Create a dataframe for total revenue
        total_revenue = pd.DataFrame({'region': ['total_revenue'], 'revenue': [filtered_data['total_revenue'].sum()]})
        print('total_revenue: ', total_revenue['revenue'])

        # Bar chart for regions' revenue
        bar_chart = alt.Chart(region_revenue).mark_bar().encode(
            x='region:N',
            y='revenue:Q',
            color='region:N'
        ).interactive()

        # Line chart for total revenue
        # Line chart for total revenue
        line_chart = alt.Chart(total_revenue).mark_rule(color='red').encode(
            y='revenue:Q',
            size=alt.value(2),  # width of the line
            tooltip=['region:N', 'revenue:Q']
        ).properties(
            width=600
        )
    

        final_chart = alt.layer(bar_chart, line_chart).resolve_scale(
                y='independent'
            ).properties(
                width=600
            ).interactive()
    return final_chart

# Streamlit app
def main():
    st.set_page_config(layout='wide')
    st.title("Line Chart from Excel Data")
    inputfile = 'test_metrics.xlsx'
    
    # Fields input
    invoice_date = "primary_datetime_dimension_value"
    revenue = "metric_value"
    region = "dimension_1_string_value"
            
    fields = {
        'x' : invoice_date,
        'y' : revenue,
        'pivot_column' : region
    }
    
    fields1 = {
        'x' : invoice_date,
        'y' : revenue,
    }
    
    # fields2 = {
    #     'x' : region,
    #     'y' : revenue,
    #     'pivot_column' : region
    # }
    
    process_response = load_data(inputfile, fields1)
    chart = line_chart(process_response, fields1)
    # chart = combined_chart(process_response, fields2)

    
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()

