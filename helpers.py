import pandas as pd

def extract_user_text_data(f):
    df = pd.read_excel(f, sheet_name=0)
    df.columns = df.columns.str.strip()
    df['Disease'] = df['Disease'].str.strip().str.lower().values
    ## retrieve the first disease name
    #print(df.loc[0, 'Disease'])
    #print(df['Disease'].values[df['Disease'].values!=df.loc[0, 'Disease']])
    ## drop na if in `Disease`
    df.dropna(subset=['Disease'], inplace=True, axis=0)
    assert pd.np.all(df['Disease'].values == df.loc[0, 'Disease'])
    disease_name = df.loc[0, 'Disease']
    ## extract relevant column list
    col_list = ['Question', 'Answer',
                'Question Score', 'Answer Score',
                'Asker ID', 'Asker Gender', 'Asker Age',
                'Answerer ID', 'Answerer Title',
                'Answerer Gender', 'Answerer Age']
    df = df[col_list]

    ## rename
    df.columns = ['question', 'answer',
                  'q_polite', 'a_polite',
                  'asker_id', 'asker_gender', 'asker_age',
                  'answerer_id', 'answerer_title', 'answerer_gender', 'answerer_age'
                 ]
    ## both patients and doctors/nurse. strip string for more coherent results
    df.asker_id = df.asker_id.str.strip().values
    df.answerer_id = df.answerer_id.str.strip().values

    ## add pair id to match question and answer (maybe not needed but let's see)
    df['qa_id'] = pd.np.arange(df.shape[0])

    #### user table
    ##### patients
    patient_df = df[['asker_id', 'asker_age', 'asker_gender']]
    ## add role
    patient_df.loc[:, 'role'] = 'patient'
    ## change column names
    patient_df.columns = ['user_id', 'age', 'gender', 'role']
    ##### doctors
    doctor_df = df[['answerer_id', 'answerer_title', 'answerer_age', 'answerer_gender']]
    ## update columns
    doctor_df.columns = ['role', 'user_id', 'age', 'gender']

    ##### append
    user_df = doctor_df.append(patient_df, ignore_index=True, sort=True)
    ## drop if `usdr_id` is missing
    user_df.dropna(subset=['user_id'], axis=0, inplace=True)
    ## drop if `gender` is missing
    user_df.dropna(subset=['gender'], axis=0, inplace=True)
    ## add id
    user_df['id'] = pd.np.arange(user_df.shape[0])

    #### text table
    ##### question
    question_df = df[['qa_id', 'question', 'asker_id', 'answerer_title', 'q_polite']]

    ## rename columns
    question_df.columns = ['qa_id', 'text', 'asker_id', 'answerer_id', 'politeness']
    ## add type
    question_df['type'] = 'q'
    ## add a column to indicate who posted
    question_df['post_user_id'] = question_df['asker_id']
    ##### answer
    answer_df = df[['qa_id', 'answer', 'asker_id', 'answerer_title', 'a_polite']]
    ## rename columns
    answer_df.columns = ['qa_id', 'text', 'asker_id', 'answerer_id', 'politeness']
    ## add type
    answer_df['type'] = 'a'
    ## add a column to indicate who posted
    answer_df['post_user_id'] = answer_df['answerer_id']


    ##### append
    text_df = question_df.append(answer_df, ignore_index=True)
    ## add disease name
    text_df['disease'] = disease_name
    ## drop if `text` field is missing
    text_df.dropna(subset=['text'], axis=0, inplace=True)
    ## drop if `post_user_id` is missing
    text_df.dropna(subset=['post_user_id'], axis=0, inplace=True)
    ## drop if not in `user_id`
    text_df = text_df.query("post_user_id in @user_df.user_id")

    return user_df, text_df
