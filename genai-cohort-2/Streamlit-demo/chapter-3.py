import streamlit  as st

st.title("Chai Taste Poll")
col1, col2 = st.columns(2)

with col1:
    st.header("Masala Chai")
    st.image("https://images.pexels.com/photos/29054033/pexels-photo-29054033/free-photo-of-elegant-overhead-view-of-tea-on-checkered-tablecloth.jpeg?auto=compress&cs=tinysrgb&w=600", width=200)
    vote1= st.button("Vote masala Chai")
    
with col2:
    st.header("Adrak Chai")
    st.image("https://images.pexels.com/photos/29565230/pexels-photo-29565230/free-photo-of-foamy-milk-tea-in-ceramic-cup-on-table.jpeg?auto=compress&cs=tinysrgb&w=600", width=200)
    vote2=st.button("Vote Adrak Chai")

if vote1: 
    st.success("Thanks for Voting Masala Chai")
elif vote2:
    st.success("Thanks for Voting Adrak Chai")


name = st.sidebar.text_input("Enter your name")
tea =  st.sidebar.selectbox("Choose your chai" , ["Masala","Adrak","keasar"])
st.success(f'Welcome {name} and yoru chai preference is {tea}, going to brewed soon!!')