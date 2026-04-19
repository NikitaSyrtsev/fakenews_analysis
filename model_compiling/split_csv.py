import pandas as pd

# Загрузите CSV-файл
input_file = 'final_data.csv'  # Замените на имя вашего файла
data = pd.read_csv(input_file)

# Определите количество строк в файле
total_rows = len(data)

# Разделите данные на две части по 50%
half = int(total_rows / 2)
first_half = data.iloc[:half]
second_half = data.iloc[half:]

# Сохраните каждую часть в отдельный CSV-файл
first_half.to_csv('first_half.csv', index=False)
second_half.to_csv('second_half.csv', index=False)

print("Файл успешно разделён на две части!")