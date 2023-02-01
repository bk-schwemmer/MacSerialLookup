# Mac Serial Lookup

# Problem
At Simply Mac, all IT assets needed to be imported into a new POS/Inventory Management System. The Purchasing Team used Apple device order numbers to
generate SKUs for each model of Mac. These order numbers were not listed in JAMF which housed all the asset serial numbers previously and there was no
easy way to pull up the order number for multiple units at once.

# Solution
I found that EveryMac.com had a public API to fetch Mac details, including order numbers. I decided to create a Flask app to automate the process so I
wouldn't have to manually lookup 600+ serial numbers. This is the Python app I created using the Flask framework. 

It retrieves the order numbers of specific Mac computers based on serial numbers and processor speeds. A Google API call was used to fetch the lists
of serial numbers and processors from a Google Sheet. An API call to EveryMac.com was then used to find the appropriate order numbers for each machine.

All design and development was completed by myself.
