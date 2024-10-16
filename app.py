import streamlit as st
import pandas as pd
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

#  Добавляем  декоратор  @st.cache_data
@st.cache_data
def  load_data():
    df  =  pd.read_csv('labeled_reviews.csv')
    return  df

# Название приложения
st.title("Анализатор отзывов о Сбербанке")

# Форма для ввода отзыва
user_review = st.text_area("Введите отзыв:", height=200)

# Кнопки для выбора анализа
analysis_type = st.radio("Выберите тип анализа:", ("Классифицировать", "Определить сентимент"))

# Загружаем размеченные данные с помощью load_data()
df  =  load_data()
# Определяем категории
categories = df['category'].unique().tolist()

# Создаем описания категорий
category_descriptions = {
    "Ипотека": "Отзывы о процессе получения ипотечного кредита в Сбербанке,  включая  проблемы  с  одобрением  заявки,  оценкой  недвижимости,  получением  траншей  и  т.д.  Также  включает  отзывы  о  сервисе  ДомКлик.",
    "Кредитные карты": "Отзывы  о  кредитных  картах  Сбербанка,  включая  проблемы  с  лимитами,  процентами,  льготным  периодом,  блокировкой  карт  и  т.д.",
    "Сбербанк Онлайн": "Отзывы  о  работе  мобильного  приложения  и  интернет-банка  Сбербанк  Онлайн,  включая  ошибки  в  приложении,  неудобный  интерфейс,  проблемы  с  доступом  и  т.д.",
    "Инвестиции": "Отзывы  об  инвестиционных  продуктах  и  услугах  Сбербанка,  включая  брокерское  обслуживание,  ПИФы,  индивидуальные  инвестиционные  счета  и  т.д.",
    "Обслуживание в отделении": "Отзывы  о  качестве  обслуживания  в  отделениях  Сбербанка,  включая  работу  сотрудников,  время  ожидания  в  очереди,  навязывание  дополнительных  услуг  и  т.д.",
    "Банкоматы": "Отзывы  о  проблемах  с  банкоматами  Сбербанка,  таких  как  зажевывание  денег,  невыдача  наличных,  технические  сбои,  длинные  очереди  и  т.д.",
    "Страхование": "Отзывы  о  страховых  продуктах  и  услугах  Сбербанка,  включая  страхование  жизни,  имущества,  ипотеки,  автомобиля  и  т.д.",
    "СберСпасибо": "Отзывы  о  программе  лояльности  СберСпасибо,  включая  начисление  и  списание  бонусов,  проблемы  с  использованием  бонусов  и  т.д.",
    "Мобильная связь": "Отзывы  о  мобильном  операторе  СберМобайл,  включая  качество  связи,  тарифы,  обслуживание  и  т.д.",
    "Другие": "Отзывы,  которые  не  относятся  к  другим  категориям.",
    "ДомКлик": "Отзывы о сервисе ДомКлик,  включая  проблемы  с  оформлением  ипотеки,  работой  менеджеров,  техническими  сбоями  и  т.д.",
    "СберПервый": "Отзывы о пакете  услуг  СберПервый.",
    "СберПремьер": "Отзывы о пакете  услуг  СберПремьер.",
    "СберМегаМаркет": "Отзывы  о  сервисе  СберМегаМаркет,  включая  проблемы  с  доставкой,  качеством  товаров,  работой  службы  поддержки  и  т.д.",
    "Сбербанк Бизнес": "Отзывы  о  сервисе  Сбербанк  Бизнес,  включая  работу  с  расчетными  счетами,  кредитами,  эквайрингом  и  т.д.",
    "Счета и вклады": "Отзывы о счетах и вкладах в Сбербанке, включая проблемы с открытием и закрытием счетов,  начислением  процентов  и  т.д.",
    "Зарплатный проект": "Отзывы  о  зарплатном  проекте  Сбербанка.",
    "Кэшбек": "Отзывы  о  кэшбеке  по  картам  Сбербанка  и  его  партнеров.",
    "Денежные переводы": "Отзывы  о  денежных  переводах  через  Сбербанк,  включая  переводы  по  номеру  телефона,  через  СБП,  за  рубеж  и  т.д.",
    "Эквайринг": "Отзывы  об  эквайринге  от  Сбербанка,  включая  работу  терминалов,  комиссии,  поддержку  и  т.д.",
    "Блокировка": "Отзывы  о  блокировке  счетов  и  карт  Сбербанка,  включая  причины  блокировки,  процедуру  разблокировки  и  т.д.",
    "Вклады": "Отзывы о вкладах в Сбербанке.",
    "ЖКХ": "Отзывы об оплате услуг ЖКХ через Сбербанк."
}

# Загружаем модель и токенизатор для Zero-Shot Classification
model_name = "facebook/bart-large-mnli"
classifier = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Загружаем предобученную модель для анализа тональности
sentiment_model = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment", max_length=512, truncation=True)

# Обработка введенного отзыва
if st.button("Анализировать"):
    if user_review:
        # Классификация по категориям
        if analysis_type == "Классифицировать":
            # Классифицируем отзыв
            results = []
            for category, description in category_descriptions.items():
                sequences = [user_review, description]
                inputs = tokenizer(sequences, padding=True, truncation=True, return_tensors="pt")
                outputs = classifier(**inputs)
                
                # Получаем  вероятность  entailment  (подтверждения)
                entailment_prob = outputs.logits.softmax(dim=1)[0][0].item()
                
                results.append((category, entailment_prob))
            
            # Находим категорию с наибольшей вероятностью
            predicted_category = max(results, key=lambda x: x[1])[0]

            st.subheader("Категория отзыва:")
            st.write(f"**{predicted_category}**")

        # Определение сентимента
        if analysis_type == "Определить сентимент":
            # Применяем модель анализа тональности
            sentiment = sentiment_model(user_review)[0]['label']
            st.subheader("Сентимент:")
            st.write(f"**{sentiment}**")
