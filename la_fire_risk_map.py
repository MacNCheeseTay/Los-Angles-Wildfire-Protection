
import numpy as np
import pandas as pd
import folium

lon_edges = np.arange(-118.952, -117.651, 0.010870) #maps west and east
lat_edges = np.arange(33.723, 34.821, 0.009009) #maps south and north

print(len(lon_edges)) #prints our pramater the column of the box of west and east
print(len(lat_edges)) #prints our pramater of north and south

WEST = -118.952
SOUTH = 33.723 #vars
LON_STEP = 0.010870 #1km expressed in degrees
LAT_STEP = 0.009009 #1km expressed in degrees
#square is 1km^2 btw (1km/1km)

def get_square(lat, lon):
  col = int((lon - WEST) / LON_STEP) #math to find square
  row = int((lat - SOUTH) / LAT_STEP)
  return col, row #returns our vars

print(get_square(34.205, -118.088))
print(get_square(34.0725, -118.5425))
#prints the square (1km^2) coords ^

mapp = folium.Map(location=[34.14205, -118.333], zoom_start=10, tiles="Esri.WorldImagery") #map, sateleite

def square_bounds(col, row): #function to calucate the boundriases
  west_edge = WEST + col * LON_STEP
  south_edge = SOUTH + row * LAT_STEP
  east_edge = west_edge + LON_STEP
  north_edge = south_edge + LAT_STEP

  folium.Rectangle(
      bounds=[[south_edge, west_edge], [north_edge, east_edge]],
      color = 'blue',
      weight = 5,
      fill = True,
      fill_opacity = 0.5
  ).add_to(mapp) #rectangle drawing

square_bounds(79, 53)
square_bounds(37, 38)#calling
mapp

history = pd.read_csv("fire_archive_SV-C2_814977.csv") # read
print(len(history))


history = history[history["type"] == 0]
print(history)

history = history.copy()

history["col"] = history.apply(lambda r: get_square(r["latitude"], r["longitude"])[0], axis=1)
history["row"] = history.apply(lambda r: get_square(r["latitude"], r["longitude"])[1], axis=1)

print(history[["latitude", "longitude", "col", "row"]].head())

history["year"] = history["acq_date"].str[0:4].astype(int)

print(history[["acq_date", "year"]].head())

years_per_square = history.groupby(["col", "row"])["year"].nunique()

print(len(years_per_square))
print(years_per_square.sort_values(ascending=False).head(10))
print(years_per_square.value_counts().sort_index())

def square_center(col, row):
  lat = SOUTH + (row + 0.5) * LAT_STEP #to find square center 
  lon = WEST + (col + 0.5) * LON_STEP
  return (lat, lon)
print(square_center(69, 47))
print(square_center(48, 22))


mapp.save("map.html")

CUTOFF = 5 #what it implies

history["years_burned"] = history.groupby(["col", "row"])["year"].transform("nunique")

print(len(history))
history = history[history["years_burned"] < CUTOFF]
print(len(history))

burned = history[["col", "row", "year"]].drop_duplicates().copy()
print(burned.head())

burned = burned.drop_duplicates().copy()
burned["burned"] = 1   # every row on this list = yes, it burned
print(len(burned))

total_rows = [] #reminder to fturue  self, checkif i did this right idk ngl 
for c in range(120):
  for r in range(122):
    for y in range(2012, 2025): 
      total_rows.append((c, r,  y))

grid = pd.DataFrame(total_rows,  columns=["col",  "row", "year"])

print(len(grid))
print(grid["year"].min(), grid["year"].max())

grid = grid.merge(burned, on=["col", "row", "year"], how="left") #matches the yes list onto calander

grid["burned"] = grid["burned"].fillna(0).astype(int) #no match ---> 0; no burn

grid = grid.sort_values(["col", "row", "year"])
grid['past_fires'] = grid.groupby(["col", "row"])["burned"].cumsum() - grid["burned"]

print(len(grid), grid["burned"].sum()) 



 #ML!!!

train = grid[(grid["year"] >= 2013) & (grid["year"] <= 2021)]
test = grid[grid["year"] >= 2022]
print(len(train), len(test))

features = ["col", "row", "past_fires"]

X_train = train[features]
y_train = train["burned"]
X_test  = test[features] #vars for the model
y_test  = test["burned"]

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix

model = DecisionTreeClassifier(max_depth=6, class_weight="balanced") #depth and weight of our model
#we are using decision tree 
model.fit(X_train, y_train) #our fitting/training

predictions = model.predict(X_test) #our predictions of the model

print(confusion_matrix(y_test, predictions)) #uh its no better than guessing/random thus we provide more info to the ML

#now we add neighbor fires
#idea: for every square and year. add up how many fires its 8 neighbots had
#imagine the 8 squares around the chessboard
nb = grid[["col", "row", "year", "past_fires"]].copy()
grid["neighbor_fires"] = 0

for dc in [-1, 0, 1]:            # shift left, none, right
    for dr in [-1, 0, 1]:        # shift down, none, up
        if dc == 0 and dr == 0:
            continue             # skip the square itself, only neighbors
        shifted = nb.copy()
        shifted["col"] = shifted["col"] + dc
        shifted["row"] = shifted["row"] + dr
        shifted = shifted.rename(columns={"past_fires": "n"})
        grid = grid.merge(shifted, on=["col", "row", "year"], how="left")
        grid["neighbor_fires"] = grid["neighbor_fires"] + grid["n"].fillna(0)
        grid = grid.drop(columns="n")

print(grid["neighbor_fires"].max())