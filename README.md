Avaya Python Scripts

I created these for monitoring and to make pulling data from the Avaya PBX easier.  Each script is mostly stand alone, in that they run by themselves.  The monitoring scripts support each other, one updates the data to a database the others read that data for the monitoring server, I used OMD which includes check_mk.

The OSSI terminals are used strongly in these scripts, I have included my word document with my notes on the OSSI commands.  This might help you make your own changes or later your own scripts.

Finally these were ran on a Avaya Communication Manager 8.1, no guarantee how they will function on anything else but knowing history odds are good.  I recommend you test on a dev server before running against production.  Also we saw issues with no maintenance resources available while running the trunk monitoring script.  I ran it once a minute.  No issues found with call processing or anything else.
