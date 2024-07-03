# Fluvius_API

## What it is
This is a simple python script that logs in to the mijn.fluvius.be portal and gets the authentication token you need to make requests to their API.

## What it does
It gets your usage details for the EAN (meter) number you provide in the code.

## How does it work?
Read the code, I added comments almost everywhere so it should be pretty much clear.

## How can I expand or define the results I want?
In your own browser, log in to mijn.fluvius.be.
Open you developer console (F12) and open the nework tab.

When you are browsing your usage, check which requests are made to the api, for example:
![image](https://github.com/sander110419/Fluvius_API/assets/13721836/a1546957-8db2-414c-b0bf-5522a208364b)

You see you get URL: https://mijn.fluvius.be/verbruik/api/consumption-histories/54144882004XXXXXXX?historyFrom=2023-06-30T22:00:00Z&historyUntil=2024-07-07T22:00:00Z&granularity=3&asServiceProvider=false

- historyFrom: should be self-explanatory.
- historyUntil: should be self-explanatory.
- granularity: some self definied fluvius variable setting the granularity of the data, but only "3" seems to work.
- asServiceProvider: having it as true also changes nothing at all.

## What does a response look like?

```

[
    {
        "sn": "1SAGXXXXXXX",
        "mdf": "2019-09-26T22:00:00Z",
        "mdu": "9999-12-30T23:00:00Z",
        "val": [
            {
                "dt": false,
                "d": "2023-06-30T22:00:00Z",
                "de": "2023-07-01T22:00:00Z",
                "oh": 0.00000000,
                "ohvs": 2,
                "ol": 13.07700000,
                "olvs": 2,
                "ih": 0.00000000,
                "ihvs": 2,
                "il": 0.00000000,
                "ilvs": 2,
                "ok": 0,
                "okvs": 0,
                "om": 0,
                "omvs": 0,
                "okgcf": null
            }
        ]
    }
]

```

## Yes, but what does it mean?

- sn: Your meters serial number
- mdf: manufacturing date?
- mdu: manufacturing date until?
- val: Here come the values
- dt: no idea
- d: date
- de: date end(?)
- oh: "Afname Dag" (XXX High is my guess)
- ohvs: no idea (could be version?)
- ol: "Afname nacht" (XXX Low is my guess)
- olvs: no idea (could be version?)
- ih: "Injectie dag" (injection high?)
- ihvs: no idea (could be version?)
- il: "Injectie nacht" (injection low?)
- ilvs: no idea (could be version?)
- ok: no idea
- okvs: no idea
- om: no idea
- omvs: no idea
- okgfc: no idea

## Can I get my consumption spikes? (piekvermogen / capaciteitstarief)
Yes! It is available under the url: https://mijn.fluvius.be/verbruik/api/consumption-spikes/54144882004XXXXXXX?historyFrom=2023-06-30T22:00:00Z&historyUntil=2024-07-07T22:00:00Z&granularity=3&asServiceProvider=false  
Make sure to use your own EAN.

## How does that output look?

```
[
    {
        "sn": "1SAG1100042062",
        "mdf": "2019-09-26T22:00:00Z",
        "mdu": "9999-12-30T23:00:00Z",
        "val": [
            {
                "d": "2023-12-31T23:00:00Z",
                "de": "2024-01-31T23:00:00Z",
                "o": 5.09800000,
                "ovs": 2,
                "tscs": "2024-01-14T11:00:00Z",
                "tecs": "2024-01-14T11:15:00Z"
            }
        ]
    }
]
```

## Yes, but what does it mean?

- sn: Your meters serial number
- mdf: manufacturing date?
- mdu: manufacturing date until?
- val: Here come the values
- d: date
- de: date end(?)
- o: Peak usage in kW
- ovs: no idea (could be version?)
- tscs: Start timestamp this peak was measured
- tecs: End timestamp this peak was measured


## Can I use this to see other peoples usage if I know their EAN?
NO, your user token only gives access to the meters you have access to in the portal. 
This is something they did do right!

## Is this legal?
Probably? This gets the same results and output as logging in to the portal and seeing the results yourself and it does not bypass any restrictions or authentication.
