# def main():
#     print("Hello from demostreamlit!")


# if __name__ == "__main__":
#     main()


import streamlit as st 
st.title("Hello Mayur App") 
st.subheader("Brewed with Streamlit") 
st.text("Welocme to your first inmteractobve app")
st.write("Choose your vaeriety of chai")

chai=st.selectbox("Your Favourite Chai: " ,["Masala Chai","Lemon Tea","Ginger Tea","Kesar tea"])
st.write(f'You Choose {chai}. Excellent choice')
st.success("Your tea has been brewed")