import pandas as pd
from xgboost import XGBRegressor

def predict_next_month_total_consumption(df_poliza, poliza_id, forecast_days=30):
    """
    Predict total water consumption for the next month (or custom number of days)
    for a given POLIZA_SUMINISTRO and return the historical + forecasted data.
    """

    # --- Feature engineering ---    
    df_poliza["lag_1"] = df_poliza["CONSUMO_REAL"].shift(1)
    df_poliza["lag_7"] = df_poliza["CONSUMO_REAL"].shift(7)
    df_poliza["rolling_mean_7"] = (
        df_poliza["CONSUMO_REAL"].shift(1).rolling(window=7).mean()
    )
    df_poliza = df_poliza.dropna().reset_index(drop=True)
    
    # --- Model training ---
    features = ["year", "month", "day", "dayofweek", "lag_1", "lag_7", "rolling_mean_7"]
    target = "CONSUMO_REAL"
    
    X = df_poliza[features]
    y = df_poliza[target]
    
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        tree_method="hist"
    )
    model.fit(X, y)
    
    # --- Forecasting ---
    last_known = df_poliza.iloc[-1].copy()
    forecast = []
    history = df_poliza.copy()

    for i in range(1, forecast_days + 1):
        next_date = last_known["FECHA"] + pd.Timedelta(days=i)

        # compute features dynamically
        recent_data = history.tail(7)["CONSUMO_REAL"]
        new_data = {
            "year": next_date.year,
            "month": next_date.month,
            "day": next_date.day,
            "dayofweek": next_date.dayofweek,
            "lag_1": history.iloc[-1]["CONSUMO_REAL"],
            "lag_7": recent_data.iloc[0] if len(recent_data) >= 7 else history.iloc[-1]["CONSUMO_REAL"],
            "rolling_mean_7": recent_data.mean()
        }

        X_future = pd.DataFrame([new_data])[features]
        next_consumption = float(model.predict(X_future)[0])

        new_row = {
            "POLIZA_SUMINISTRO": poliza_id,
            "FECHA": next_date,
            "CONSUMO_REAL": next_consumption,
            "year": next_date.year,
            "month": next_date.month,
            "day": next_date.day,
            "dayofweek": next_date.dayofweek,
            "is_forecast": True
        }

        forecast.append(new_row)
        # Add predicted value to history for recursive feature updates
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    forecast_df = pd.DataFrame(forecast)
    
    # Add flag to original data
    df_poliza["is_forecast"] = False

    # Combine original + forecasted data
    df_extended = pd.concat([df_poliza, forecast_df], ignore_index=True).sort_values("FECHA")
    total_consumption = forecast_df["CONSUMO_REAL"].sum()

    return total_consumption, forecast_df, df_extended


def call_predict_next_month_total_consumption(df, poliza_id, forecast_days=30): 
    """
    Wrapper to filter data by POLIZA_SUMINISTRO and call the prediction function.
    """
    df_ = df[["POLIZA_SUMINISTRO", "FECHA", "CONSUMO_REAL"]].copy()

    # --- Filter for the given POLIZA ---
    df_poliza = df_[df_["POLIZA_SUMINISTRO"] == poliza_id].copy()
    if df_poliza.empty:
        raise ValueError(f"No data found for POLIZA_SUMINISTRO = {poliza_id}")

    df_poliza["FECHA"] = pd.to_datetime(df_poliza["FECHA"])
    df_poliza = df_poliza.sort_values(by="FECHA").reset_index(drop=True)

    # --- Add temporal features ---
    df_poliza["year"] = df_poliza["FECHA"].dt.year
    df_poliza["month"] = df_poliza["FECHA"].dt.month
    df_poliza["day"] = df_poliza["FECHA"].dt.day
    df_poliza["dayofweek"] = df_poliza["FECHA"].dt.dayofweek

    total_consumption, forecast_df, df_extended = predict_next_month_total_consumption(
        df_poliza, poliza_id, forecast_days
    )

    return total_consumption, forecast_df, df_extended

def euros_per_m3(liters, service_type):
    m3 = liters/1000
    price = 0
    if service_type == "D": 
        if 0 <= m3 <= 6: price = m3*0.8
        elif 6 < m3 <= 9: price = m3 * 1.6002
        elif 9 < m3 <= 15: price = m3 * 2.4894
        elif 15 < m3 <= 18: price = m3 * 3.3189
        elif 18 < m3: price= m3 * 4.1486

    elif service_type == "C":
        if 0 <= m3 <= 9: price = m3 * 1.2164
        elif m3 >= 9: price = m3 * 2.4328

    elif service_type == "A":       #mirar que es exactamente 
        price = m3 * 1.1173 
    return price


    
    