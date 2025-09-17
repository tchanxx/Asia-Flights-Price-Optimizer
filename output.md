## Economy Summary price table (USD):
```
Window | with_SHA    | without_SHA
----------------------------------
early  | $2562       | $3178      
mid    | $2312       | $2410      
late   | $2592       | $2635 
```

## Premium Economy Summary price table (USD):
```
Summary price table (USD):
Window | with_SHA    | without_SHA
----------------------------------
early  | $4118       | $4738      
mid    | $3618       | $4345      
late   | $3019       | $4735  
```

## Itineraries in economy summary table:
```
[1] $2562 | window=early | include_SHA=True
    Route: NYC -> TYO -> SHA -> TPE -> HKG -> NYC
    Nights: TYO:4n, SHA:4n, TPE:5n, HKG:5n
    Start: 2025-12-10  End: 2026-01-03  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-10 arrive 2025-12-11 $835
      TYO->SHA  depart 2025-12-15 arrive 2025-12-16 $120
      SHA->TPE  depart 2025-12-21 arrive 2025-12-22 $69
      TPE->HKG  depart 2025-12-27 arrive 2025-12-28 $48
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $1490

[2] $3178 | window=early | include_SHA=False
    Route: NYC -> TPE -> TYO -> HKG -> NYC
    Nights: TPE:4n, TYO:4n, HKG:5n
    Start: 2025-12-10  End: 2026-01-03  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TPE  depart 2025-12-11 arrive 2025-12-12 $1230
      TPE->TYO  depart 2025-12-16 arrive 2025-12-17 $120
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $1490

[3] $2312 | window=mid | include_SHA=True
    Route: NYC -> TYO -> SHA -> HKG -> TPE -> NYC
    Nights: TYO:5n, SHA:4n, HKG:5n, TPE:4n
    Start: 2025-12-16  End: 2026-01-09  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-16 arrive 2025-12-17 $965
      TYO->SHA  depart 2025-12-22 arrive 2025-12-23 $120
      SHA->HKG  depart 2025-12-27 arrive 2025-12-28 $120
      HKG->TPE  depart 2026-01-02 arrive 2026-01-03 $67
      TPE->NYC  depart 2026-01-08 arrive 2026-01-09 $1040

[4] $2410 | window=mid | include_SHA=False
    Route: NYC -> TYO -> HKG -> TPE -> NYC
    Nights: TYO:4n, HKG:5n, TPE:4n
    Start: 2025-12-16  End: 2026-01-09  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-16 arrive 2025-12-17 $965
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->TPE  depart 2026-01-02 arrive 2026-01-03 $67
      TPE->NYC  depart 2026-01-08 arrive 2026-01-09 $1040

[5] $2592 | window=late | include_SHA=True
    Route: NYC -> TYO -> HKG -> SHA -> TPE -> NYC
    Nights: TYO:4n, HKG:5n, SHA:4n, TPE:4n
    Start: 2025-12-21  End: 2026-01-14  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-22 arrive 2025-12-23 $1190
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->SHA  depart 2026-01-02 arrive 2026-01-03 $120
      SHA->TPE  depart 2026-01-07 arrive 2026-01-08 $69
      TPE->NYC  depart 2026-01-13 arrive 2026-01-14 $875

[6] $2635 | window=late | include_SHA=False
    Route: NYC -> TYO -> HKG -> TPE -> NYC
    Nights: TYO:4n, HKG:5n, TPE:4n
    Start: 2025-12-21  End: 2026-01-09  (≈ 20 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-22 arrive 2025-12-23 $1190
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->TPE  depart 2026-01-02 arrive 2026-01-03 $67
      TPE->NYC  depart 2026-01-08 arrive 2026-01-09 $1040
```

## Itineraries in premium economy summary table:
```
[1] $4118 | window=early | include_SHA=True
    Route: NYC -> SHA -> TYO -> TPE -> HKG -> NYC
    Nights: SHA:4n, TYO:5n, TPE:5n, HKG:5n
    Start: 2025-12-10  End: 2026-01-03  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->SHA  depart 2025-12-10 arrive 2025-12-11 $1200
      SHA->TYO  depart 2025-12-15 arrive 2025-12-16 $120
      TYO->TPE  depart 2025-12-21 arrive 2025-12-22 $120
      TPE->HKG  depart 2025-12-27 arrive 2025-12-28 $48
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $2630

[2] $4738 | window=early | include_SHA=False
    Route: NYC -> TPE -> TYO -> HKG -> NYC
    Nights: TPE:4n, TYO:4n, HKG:5n
    Start: 2025-12-10  End: 2026-01-03  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TPE  depart 2025-12-11 arrive 2025-12-12 $1650
      TPE->TYO  depart 2025-12-16 arrive 2025-12-17 $120
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $2630

[3] $3618 | window=mid | include_SHA=True
    Route: NYC -> TYO -> TPE -> HKG -> SHA -> NYC
    Nights: TYO:5n, TPE:5n, HKG:5n, SHA:4n
    Start: 2025-12-15  End: 2026-01-08  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-15 arrive 2025-12-16 $1760
      TYO->TPE  depart 2025-12-21 arrive 2025-12-22 $120
      TPE->HKG  depart 2025-12-27 arrive 2025-12-28 $48
      HKG->SHA  depart 2026-01-02 arrive 2026-01-03 $120
      SHA->NYC  depart 2026-01-07 arrive 2026-01-08 $1570

[4] $4345 | window=mid | include_SHA=False
    Route: NYC -> TYO -> HKG -> TPE -> NYC
    Nights: TYO:4n, HKG:5n, TPE:4n
    Start: 2025-12-16  End: 2026-01-09  (≈ 25 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-16 arrive 2025-12-17 $2010
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->TPE  depart 2026-01-02 arrive 2026-01-03 $67
      TPE->NYC  depart 2026-01-08 arrive 2026-01-09 $1930

[5] $3019 | window=late | include_SHA=True
    Route: NYC -> SHA -> HKG -> TYO -> TPE -> NYC
    Nights: SHA:4n, HKG:5n, TYO:4n, TPE:4n
    Start: 2025-12-22  End: 2026-01-14  (≈ 24 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->SHA  depart 2025-12-22 arrive 2025-12-23 $1200
      SHA->HKG  depart 2025-12-27 arrive 2025-12-28 $120
      HKG->TYO  depart 2026-01-02 arrive 2026-01-03 $89
      TYO->TPE  depart 2026-01-07 arrive 2026-01-08 $120
      TPE->NYC  depart 2026-01-13 arrive 2026-01-14 $1490

[6] $4735 | window=late | include_SHA=False
    Route: NYC -> TYO -> HKG -> TPE -> NYC
    Nights: TYO:4n, HKG:5n, TPE:4n
    Start: 2025-12-18  End: 2026-01-09  (≈ 23 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-18 arrive 2025-12-19 $2400
      TYO->HKG  depart 2025-12-27 arrive 2025-12-28 $338
      HKG->TPE  depart 2026-01-02 arrive 2026-01-03 $67
      TPE->NYC  depart 2026-01-08 arrive 2026-01-09 $1930
```