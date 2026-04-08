import pandas as pd
import glob
import os
from tqdm import tqdm
import xgboost as xgb  
from sklearn.model_selection import train_test_split
import joblib

# 1. Path & Import (Keeping your existing logic)
path = r'D:\IDS\data' 
all_files = glob.glob(os.path.join(path, "*.csv"))

li = []
print(f"Found {len(all_files)} files. Starting import...")
for filename in tqdm(all_files, desc="Reading Files"):
    df = pd.read_csv(filename, index_col=None, header=0, low_memory=False)
    li.append(df)

full_df = pd.concat(li, axis=0, ignore_index=True)

# 2. Data Cleaning
full_df.columns = [c.strip().lower() for c in full_df.columns]
full_df.replace([float('inf'), float('-inf')], 0, inplace=True)
full_df.dropna(inplace=True)

# 3. Feature Selection
features = ['destination port', 'flow duration', 'total fwd packets', 'total backward packets']
target = 'label'

# Convert text labels to numbers (Essential for XGBoost)
if full_df[target].dtype == 'object':
    print("Converting text labels to numbers...")
    full_df[target] = full_df[target].astype('category').cat.codes

X = full_df[features]
y = full_df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. GPU Training Logic
print(f"🚀 Training on GPU using {len(X_train)} rows...")

# tree_method='hist' and device='cuda' tells XGBoost to use your NVIDIA GPU
model = xgb.XGBClassifier(
    tree_method='hist',
    device='cuda', 
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)

# 5. Save the Model
joblib.dump(model, 'ids_model.pkl')
print("✅ Success! GPU-trained 'ids_model.pkl' created in D:\IDS")