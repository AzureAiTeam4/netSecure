import pandas as pd

df = pd.read_csv('data/data/cleaned_dataset.csv')

df_attack = df[df['Label'] == 1].copy()
df_attack = df_attack.drop(columns=['Label'])

print(f'shape: {df_attack.shape}')
print(df_attack['Attack_label'].value_counts())

df_attack.to_csv('data/data/attack_only_dataset.csv', index=False)
print('저장 완료')
