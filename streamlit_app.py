import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm
import uuid

st.set_page_config(page_title="ChatAI", page_icon="https://emojix.s3.ap-northeast-1.amazonaws.com/g3/svg/1f4ac.svg")

# サイドバーにAPIキーの入力フィールドを追加
api_key = st.sidebar.text_input("APIキーを入力してください", type="password")

# セッション状態の初期化
if "api_key" not in st.session_state:
    st.session_state["api_key"] = None

# APIキーが入力された場合、それをセッションに保存し、GeminiのAPIを設定
if api_key:
    st.session_state["api_key"] = api_key
    genai.configure(api_key=st.session_state["api_key"])

# APIキーが入力されていない場合は、警告を表示し、以降の機能は無効化
if st.session_state["api_key"] is None:
    st.warning("APIキーを入力すると、チャットを開始できます。")
else:
    # セッション状態の初期化
    if "chat_sessions" not in st.session_state:
        st.session_state["chat_sessions"] = {}
        st.session_state["current_chat_id"] = None

    # ユーザーとアシスタントのアイコンを設定
    user_icon_url = "https://emojix.s3.ap-northeast-1.amazonaws.com/g3/svg/1f60a.svg"  # ユーザーアイコンのURLを指定
    assistant_icon_url = "https://emojix.s3.ap-northeast-1.amazonaws.com/g3/svg/1f916.svg"  # アシスタントアイコンのURLを指定

    # 新しいチャットセッションを作成する関数
    def create_new_chat():
        chat_id = str(uuid.uuid4())
        model = genai.GenerativeModel('gemini-pro')
        st.session_state["chat_sessions"][chat_id] = {
            "chat_session": model.start_chat(history=[
                glm.Content(role="user", parts=[glm.Part(text="あなたは優秀なAIアシスタントです。できるだけわかりやすく説明してください。またわからないことはわからないと言ってください。")]),
                glm.Content(role="model", parts=[glm.Part(text="わかりました。")])
            ]),
            "chat_history": []
        }
        st.session_state["current_chat_id"] = chat_id

    # ホームに戻るための関数
    def return_to_home():
        st.session_state["current_chat_id"] = None

    # サイドバーに「ホームに戻る」ボタンを追加
    if st.sidebar.button("ホーム"):
        return_to_home()

    # サイドバーに「＋」ボタンを追加
    if st.sidebar.button("＋"):
        create_new_chat()

    # 既存のチャットセッションをサイドバーにボタンとして表示
    if st.session_state["chat_sessions"]:
        st.sidebar.write("チャット一覧:")
        for chat_id in st.session_state["chat_sessions"]:
            if st.sidebar.button(f"チャット {chat_id[:8]}"):
                st.session_state["current_chat_id"] = chat_id
    else:
        st.sidebar.write("チャットがありません")

    # カスタムCSSスタイルの定義
    st.markdown("""
        <style>
        .user-message {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 10px;
        }
        .assistant-message {
            display: flex;
            justify-content: flex-start;
            margin-bottom: 10px;
        }
        .message {
            max-width: 80%;
            padding: 10px;
            border-radius: 10px;
            position: relative;
            margin: 5px;
            font-size: 16px;
        }
        .user-bubble {
            background-color: #dcf8c6;
            border-radius: 10px 0px 10px 10px;
        }
        .assistant-bubble {
            background-color: #f1f1f1;
            border-radius: 0px 10px 10px 10px;
        }
        .avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin: 5px;
        }
        .user-avatar {
            margin-left: 5px;
        }
        .assistant-avatar {
            margin-right: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

    # 現在のチャットセッションの表示またはホームページの表示
    if st.session_state["current_chat_id"]:
        current_chat = st.session_state["chat_sessions"][st.session_state["current_chat_id"]]
        chat_session = current_chat["chat_session"]
        chat_history = current_chat["chat_history"]

        # チャット履歴を全て表示
        for message in chat_history:
            if message["role"] == "user":
                # ユーザーメッセージを右側に表示（アイコンは右）
                st.markdown(f"""
                <div class="user-message">
                    <div class="message user-bubble">
                        {message["content"]}
                    </div>
                    <img src="{user_icon_url}" class="avatar user-avatar" alt="User Icon">
                </div>
                """, unsafe_allow_html=True)
            else:
                # アシスタントメッセージを左側に表示（アイコンは左）
                st.markdown(f"""
                <div class="assistant-message">
                    <img src="{assistant_icon_url}" class="avatar assistant-avatar" alt="Assistant Icon">
                    <div class="message assistant-bubble">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ユーザー入力送信後処理
        if prompt := st.chat_input("ここに入力してください"):
            # ユーザの入力を表示する
            chat_history.append({"role": "user", "content": prompt})
            st.markdown(f"""
            <div class="user-message">
                <div class="message user-bubble">
                    {prompt}
                </div>
                <img src="{user_icon_url}" class="avatar user-avatar" alt="User Icon">
            </div>
            """, unsafe_allow_html=True)

            # Genimi Proにメッセージ送信
            response = chat_session.send_message(prompt)

            # アシスタントのレスポンスを表示
            chat_history.append({"role": "assistant", "content": response.text})
            st.markdown(f"""
            <div class="assistant-message">
                <img src="{assistant_icon_url}" class="avatar assistant-avatar" alt="Assistant Icon">
                <div class="message assistant-bubble">
                    {response.text}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # ホームページを表示
        st.title("ChatAIへようこそ")
        st.write("ここでは、Google Gemini APIを使用してAIアシスタントとチャットを行うことができます。")
        st.write("サイドバーから新しいチャットセッションを作成し、会話を開
