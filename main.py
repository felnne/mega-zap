import streamlit as st

def show_intro() -> None:
    st.title("🎈 Mega Zap!")

def main():
    st.set_page_config()
    show_intro()

if __name__ == "__main__":
    main()
