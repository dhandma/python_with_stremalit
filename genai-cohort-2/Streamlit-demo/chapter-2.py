import streamlit  as st

st.title("ChaiMaker!!")
st.subheader("This is a basic chai maker app")

if st.button("Make chai"):
    st.success("Your chai is being brewed")


add_masala= st.checkbox("Add Masala")
if add_masala: 
    st.write("Masala added to your tea")

tea_type=st.radio("Select one add-on " , ['Milk','water','Almond Milk'] )

st.write("Selected base ", tea_type)
flavour =  st.selectbox("Choose flavour ", ["Adrak","Masala","Tuksi"])
st.write("Flvour selected by you ",flavour)

#range input
sugar_slider = st.slider("Sugar Level", 0, 5 , 2)
st.write("Selected sugar level ", sugar_slider)

#no input
cups=st.number_input("How many cups" , min_value=1, max_value=10,step=1)

st.write("Numver of collected cups ", cups)

#text input
name = st.text_input("Enter your name")

if name:
    st.write(f'Welcome {name}!, your chai is going to brewed soon, please enjoy the cafe!!')

dob=st.date_input("Select your data of birth")
st.write("Your Date of Birth is ", dob)