# Designer로 넘길 최종 파일 생성
import pandas as pd

df = pd.read_csv('data/data/cleaned_dataset.csv')
df = df.drop(columns=['Attack'])  # 문자열 컬럼 불필요
df.to_csv('data/data/final_dataset.csv', index=False)
print(df.shape)  # (4500000, 55)