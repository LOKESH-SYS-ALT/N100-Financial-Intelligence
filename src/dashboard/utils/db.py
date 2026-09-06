import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def get_companies():
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM companies
        """,
        conn,
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):
    conn = get_connection()

    if year is None:
        query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY id
        """

        df = pd.read_sql(
            query,
            conn,
            params=[ticker],
        )

    else:
        year_text = str(year)

        # Prefer March financial year.
        query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
          AND year = ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=[
                ticker,
                f"Mar {year_text}",
            ],
        )

        # Fallback to TTM if March data is unavailable.
        if df.empty:
            df = pd.read_sql(
                """
                SELECT *
                FROM financial_ratios
                WHERE company_id = ?
                  AND year = 'TTM'
                """,
                conn,
                params=[ticker],
            )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_pl(ticker):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_bs(ticker):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_cf(ticker):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sectors():
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM sectors
        """,
        conn,
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peers(group_name):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        conn,
        params=[group_name],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_valuation(ticker, year=None):
    conn = get_connection()

    if year is None:
        df = pd.read_sql(
            """
            SELECT *
            FROM market_cap
            WHERE company_id = ?
            ORDER BY year
            """,
            conn,
            params=[ticker],
        )
    else:
        df = pd.read_sql(
            """
            SELECT *
            FROM market_cap
            WHERE company_id = ?
              AND year = ?
            """,
            conn,
            params=[ticker, int(year)],
        )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_peer_company_ids():
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT DISTINCT company_id
        FROM peer_groups
        WHERE company_id IS NOT NULL
        ORDER BY company_id
        """,
        conn,
    )

    conn.close()

    return df