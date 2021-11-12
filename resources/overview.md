# Western Power Distribution Data Challenge (Part 1)

## Learn the Details

### Challenge Overview

This is the first of three Western Power Distribution (WPD) short data challenges! The aims of these challenges include:

1. Demonstrating the value in making data openly available
2. Increasing the visibility of some of the challenges network operators face
3. Increase the understanding of the different ways to tackle some of these problems
4. Providing high quality and accurate benchmarks with which to enable innovation and research

Note all the slides from the kick-off and other information can be found on our [LinkedIn group](https://www.linkedin.com/groups/9025332/) 

<br>

### Challenge 1: High Resolution Peak Estimation

This initial challenge aims to understand how accurately high resolution features can be estimated given only information from lower resolution data. Specifically we are asking participants to estimate the highest peak value and lowest trough at a one minute resolution within each half hourly period given only half hourly measurements. This is an interesting problem to a distribution network operator as the spikes in demand can mean strain on their network. Such issues may become increasingly common, especially on the lower voltages of the network, due to the expanding use of lower carbon technologies such as electric vehicles, and heat pumps. However, monitoring can be expensive (especially in the long term) as it requires investment in additional storage, communications equipment and processing units.

<br>

### Problem Setup

The scenario presented by this challenge is whether limited higher resolution monitoring can be used to estimate future high resolution demand spikes when the high resolution is no longer available. Participants are asked to estimate the largest and smallest demand at one minute for each half hour over the test period (a month) given the lower resolution demand data (which is at half hourly resolution), and accompanying weather data. To develop and train the models about 2 years of historical data have also been provided and a validation phase (the month prior to the test period) has also been provided which also serves to test the submission process. In addition the actual historical high resolution data will also be available for the dates prior to the validation/test periods. The evaluation metric is a skill score which measures the difference between the actual value and your estimated value, scaled according to a benchmark model (see Evaluation page for more details).

<br>

### Validation Phase

To help participants get used to the submission process and better understand the problem there will be a validation phase which runs for a two week period from 11th November 2021 to 25th November 2021 (midnight). This phase allows unlimited submissions and can help you test and refine your models. For the Validation phase teams are asked to estimate the maximum and minimum at one minute resolution for every half hour of the month of August 2021. In other words the aim is to estimate a total of 2976 values (2 values per half hour for each day (31) of the month). Results from this phase will not be used to determine your overall ranking for the challenge.

<br>

### Testing Phase

The testing phase will run from 26th November 2021 to 10th December 2021 (midnight). You will be asked to estimate the same values for September 2021 (note that due to data limitations the hours after 10am on 30th September are not included). During this stage you will be limited to six submissions. This phase will be used to judge your success and ranking for the challenge.

<br>

### Teams

We are allowing teams of up to 5 individuals. To group yourself in a team you need to follow the codalab guidance found here. Note that all team members can make submissions during Phase 1, but we ask that only a single nominated team member make submissions during Phase 2.

<br>

### Data

The substation data is hosted on the WPD data portal and can be found [here](https://connecteddata.westernpower.co.uk/dataset/western-power-distribution-data-challenge-1-high-resolution-peak-estimation). MERRA-2 weather data from locations close to the substations can be found as public data under the participate then files tab. More details of the data are in the data tab. The license terms for usage of the data can be found [here](https://www.westernpower.co.uk/open-data-licence) and [here](https://disc.gsfc.nasa.gov/information/documents?title=data-policy).

<br>

### How to Submit

The data must submitted via a zip file of a CSV file with your maximum and minimum predictions. Templates for your submission can be found here. The CSV must be renamed "Predictions" before zipping in order to be evaluated. 

<br>

### Prizes

The winners of this challenge will receive credit worth £500 for a cloud computing service (e.g. AWS). The top three teams/individuals from Phase 2 will be invited to present their methodologies in a webinar.

<br>
<br>

## Data Overview

This section gives further details about the data which is available for the challenge. The substation data can be accessed from the WPD data portal which is available [here](https://connecteddata.westernpower.co.uk/dataset/western-power-distribution-data-challenge-1-high-resolution-peak-estimation). The local weather data can found as public data under the files tab.

The data consists of the following files:

* Half hourly demand data: These are 30 minute resolution demand data, and is from the dates 01/11/2019 to 10am on 30/09/2021. It will be treated as being known for those periods and could be used as an input to the models. It comes from a single feeder on a substation at Staplegrove (latitude 51.0254, longitude -3.1204). (Stored in filenames: MW_Staplegrove_CB905_MW_observation_variable_half_hourly_real_power_MW_pre_august.csv, MW_Staplegrove_CB905_MW_observation_variable_half_hourly_real_power_MW_august.csv and MW_Staplegrove_CB905_MW_observation_variable_half_hourly_real_power_MW_september.csv)
* Half hourly peak and trough data: This is 30 minute resolution data for the maximum and minimum of minute demand in the half hour that follows. This is the unknown that you are trying to estimate and so only covers the period from 01/11/2019 to 31/07/2021. August’s data will be released at the end of the first phase. (Stored in filename: MW_Staplegrove_CB905_MW_target_variable_half_hourly_max_min_real_power_MW_pre_august.csv)
* High Resolution one minute demand data: These are 1 minute resolution data from 01/11/2019 to 31/07/2021. This is the data that was used to create the above data as described in detail below. You may use this as you wish to inform you modelling. This data also includes some additional attributes that were not directly used in the creation of the previous data which you may or may not find useful. August’s data will be released at the end of the first phase. (Stored in filename: MW_Staplegrove_CB905_MW_minute_real_power_MW_pre_august.csv)
* Weather Data: These are hourly data that consists of reanalysis temperature, wind speed (North and East), pressure, irradiance and humidity from 5 locations around the substation. Since demand is often effected by weather these variables may be useful as inputs for you models and more generally in model development. (Stored in file names: df_staplegrove_1_hourly.csv, df_staplegrove_2_hourly.csv, df_staplegrove_3_hourly.csv, df_staplegrove_4_hourly.csv, df_staplegrove_5_hourly.csv):
* Similar data for two other feeders on the following substations: Mousehole (50.0838, -5.5487) and Geevor (50.1489,-5.6730). These may also be useful in the development of your models. However, results from these feeders will not be assessed as part of the challenge. 
* Other data: No other external data may be used as part of this challenge. Later challenges are likely to include the use of external data under certain restrictions. 

Data up to the beginning of August 2021 will be used for training. For the validation phase of the challenge you will be asked to estimate the half hourly peaks and troughs for August 2021. This will be followed by testing phase that will involve estimating the half hourly peaks and troughs for September 2021.

<br>

### Demand Data

The demand data comes from a single feeder on a substation at Staplegrove (51.0254, -3.1204). The data comes in three forms:

* The original one minute monitoring data. This is available only for the training period up to the beginning of August.
* The half hourly version of the demand, which is derived from the one minute data for this example. This is available for the training, validation and test periods up to the end of September.
* The half hourly version of the peak and trough demand, which is also derived from the one minute data for this example. This is the target variable which you are trying to estimate. This is available only for the training period up to the beginning of August.

All this data has been shifted to UTC time to make it readily joinable with the Weather data (see below).

More information is available on the substation from WPD's Network Capacity Map. This shows lots of information including key asset ratings and location information and can be found [here](https://connecteddata.westernpower.co.uk/dataset/wpd-network-capacity-map/resource/d1895bd3-d9d2-4886-a0a3-b7eadd9ab6c2?filters=Substation_Name%3AStaplegrove). This shows breakdown of generation on the feeder is Hydro 13kVA, Mixed 8.68kVA, Photovoltaic 6433.9kVA, and Storage (Battery) 3.68kVA. This shows that there is quite a bit of PV connected. You will notice that this feeder has some negative demand due to this high amount of generation. This will result in reverse flows of energy back up the distribution network. Hence for this particular feeder it is useful to know both the maximum demand and the minimum demand (which may be negative). It also means that solar irradiance weather data may be particularly useful for this task.

In addition the following tables shows the number of customers from each profile class on the feeder.

| Profile Class                                                |   Number of Customers |
|:-------------------------------------------------------------|----------------------:|
| 1 (domestic unrestricted)                                    |                  8066 |
| 2 (domestic economy 7)                                       |                   952 |
| 3 (non-domestic unrestricted)                                |                   499 |
| 4 (non-domestic economy 7)                                   |                   105 |
| 5 (Non-dom , max demand customerswith Peak Load factor <20%) |                     0 |
| 6 (Non-dom , max demand with PLFbetween 20 and 30%)          |                     1 |
| 7 (Non-dom , max demand with PLFbetween 30 and 40%)          |                     2 |
| 8 (Non-dom , max demand with PLFover 40%                     |                     6 |
    

More details of the profile classes can be found [here](https://www.elexon.co.uk/knowledgebase/profile-classes/).
    
<br>

### Half Hourly Data Creation

Both sets of half hourly data were created using the ‘time’ and ‘value’ columns from the one minute data. Only data labelled as ‘Good’ in the ‘quality’ column were used to create the half hourly data. The half hourly demand data are created by taking the mean of the 30 individual minutes following the time point (i.e. for 11:30 it will be the mean for 11:30 to 11:59). The half hourly peak and trough data is created by taking the maximum and minimum value in the 30 individual minutes following the time point. Where some data is missing (or not ‘Good’) within that half hour then only the available data is used. Where no data is available for a half hour the gaps that occur are filled using linear interpolation of the calculated half hourly mean/max/min values.

Note on outliers: we have not removed any outliers in preprocessing these data, preferring instead to leave this as something you may want to investigate. However we have visually inspected the one minute data for the validation and test periods (August and September) and it appears to be outlier free and so scoring is unlikely to be affected by them.

<br>

### High Resolution One Minute Demand Data

This is the standard one minute monitoring data that can be provided for a feeder. You won't necessarily be able to explicitly use this data as part of the training/validation process, but it is provided to aid with data exploration and understanding. The following are a brief description of the columns within that data:

* attrId – Substation data stream ID
* maxtime – The time of the peak sample readings taken during the minute.
* maxvalue – The peak real power reading taken during the minute in MW.  
* mintime – The time of the minimum sample readings taken during the minute.
* minvalue – The minimum real power reading taken during the minute in MW.  
* Quality  –  ‘Good’ is  data quality is considered good for the minute, ‘Bad’ is data quality is considered bad for the minute, ‘Good Ip’ is the communications were considered good for that minute and ‘Bad Ip’ is the communications were considered bad for that minute.
* samplecount – The number of sample readings made during the minute.
* time – Start of the minute over which the data is sampled. i.e. 12:00 is sampled from 12:00:00 to 12:00:59
* units – In the data this is always 9, which means all data is in MW.
* value – The mean of the samples taken by the measuring device during that minute in MW.

This data is in the raw form provided by WPD's monitoring system, except that the time has been converted to UTC.

<br>

### Weather Data

The weather data has been collected using MERRA-2 reanalysis weather data. Reanalysis weather data are estimates of weather variables at the numerical weather prediction grid points based on assimilation of historical weather data. We provide the following weather variables at hourly resolution for the period 1st January 2019 to 30th September 2021:

| Variable             | Units                          | Description                                    | MERRA Database   | MERRA field ID   |
|:---------------------|:-------------------------------|:-----------------------------------------------|:-----------------|:-----------------|
| Temperature          | Celcuis                        | Instantaneous temperature reading              | inst1_2d_asm_Nx  | T2M              |
| Solar Irradiance     | W m-2 (watts per square meter) | Surface incoming shortwave flux                | tavg1_2d_rad_Nx  | SWGDN            |
| Eastward Wind Speed  | m s-1                          | Average (2-meter) Wind Speed in East Direction | tavg1_2d_slv_Nx  | U2M              |
| Northward Wind Speed | m s-1                          | Average (2-meter) Wind Speed North Direction   | tavg1_2d_slv_Nx  | V2M              |
| Surface Pressure     | Pa                             | Average Surface Pressure                       | tavg1_2d_slv_Nx  | PS               |
| Specific Humidity    | kg kg-1                        | Average 2-meter specific humidity              | tavg1_2d_slv_Nx  | QV2M             |

If you are interested in more details regarding the variables then you can use the MERRA database and field IDs given in the table and search the MERRA-2 documentation given [here](https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf). The irradiance data is time-averaged over the next hour period (e.g. 10:00 AM time stamps means the period 10:00 to 11:00 AM), but the temperature is an instantaneous value at each hour of the day. The time stamps refer to UTC.

The locations correspond to grid points on the numerical weather prediction grid. There are five weather grid points, given by locations:

| Name          |   Latitude |   Longitude |
|:--------------|-----------:|------------:|
| staplegrove_1 |       51   |      -3.125 |
| staplegrove_2 |       51   |      -2.5   |
| staplegrove_3 |       51.5 |      -3.125 |
| staplegrove_4 |       51.5 |      -2.5   |
| staplegrove_5 |       51   |      -3.75  |

Unlike some of the demand data, these data will be known and so can be treated as observation data throughout. 

We have also provided demand data for two other sites for pratice if desired. Hence we have also extracted the same weather data for this site (Called Mousehole) in the following locations:

| Name        |   Latitude |   Longitude |
|:------------|-----------:|------------:|
| mousehole_1 |       50   |      -5.625 |
| mousehole_2 |       50   |      -5     |
| mousehole_3 |       50.5 |      -5.625 |
| mousehole_4 |       50.5 |      -5     |
| mousehole_5 |       50.5 |      -4.375 |

Weather data is not provided for Geevor, but it is in a similar geographical location to Mousehole.

This data is sourced from the [MERRA-2 dataset](https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/) and provided under the terms of their [data policy](https://disc.gsfc.nasa.gov/information/documents?title=data-policy).