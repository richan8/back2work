#Project 4 : Going Back to Work
##Description:
AI-powered decision system responds giving the requestor a decision. Each decision is either an accept, manifested with a QR code with the address and allowed arrival and departure times in text or a downright reject. The departure time is needed since the system must preserve building density and people must leave the building to make “space” for others to enter. The security personnel or receptionists supervise a programmable scanner or manually scan the QR code to allow entrance and exit (pretty similar to the scanners used to allow entry of an aircraft at the gate). The system also allows for group bookings, made by an assistant for example, to enable face to face meetings. In this case the decision system accepts or rejects for the whole group.


We have developed a web app using python,flask,mongodb and deployed it using heroku. 
The URL to deployed instance is-
https://back-2-work.herokuapp.com/


Link to our Colab Notebook-
https://colab.research.google.com/drive/1AFsYUkObd7Zpoa3dN1hW9nlM2V-9TDAo

Link to the video of working of the app-
https://drive.google.com/open?id=1fv_2yt1-VfFQHcqv4Oh4wrmxwrcl58jq

#Assumptions -
1)We have considered three years of data(2019,2018,2017) from https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page website
2)We assume that the drop-off location id(DULocationID) is an individual building to which user will request access to
3)We only consider 4 DULocations(161,162,163,164) that are in MidTown Manhattan to avoid computational complexity

#Steps-
##1)Data Pre-Processing(colab notebook)
    Read all files of each month for a particular year and made a combined csv file for a year.
    Filter out NA values and the values that do not belong to the same year
    Necessary type conversion needs to be done. Seperating date and time columns.
    Writing data into the final 'year'.csv file.
##2)Optimal Decision Policy & Algorithm(app.py)
    We calculate the total no.of people present at the requested location in the same time duration in the previous three years.
    Calculate the mean over the three years and divide it by 3 to follow the guidelines provided by CDC of maintaining a workforce of       33% in public places , which would be the threshold of that location for the current datetime.
      If the current population of the location retrived from the database +the number of people in the request exceeds the threshold we       would deny the request
      Else we will allow the user to enter the location by sending a QR code to the user. Update the current population.
##3)App Deployement
    Integrates the algorithm with the deployed app using heroku and setup the autodeploy functionality which enables any changes in the     master branch will be auto deployed on the same instance of heroku.


Submitted by:
Aishwarya Kore(adk497)
Richanshu Jha(rj1469)
Sunny Bansal(sb7004)

