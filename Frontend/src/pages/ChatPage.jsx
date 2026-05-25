import Sidebar from "../components/Sidebar";
import { useState, useRef, useEffect } from "react";

export default function ChatPage() {
  const user = {
    name: "",
    _id: "demo-user",
  };

  const createWelcomeMessage = () => ({
    id: Date.now(),
    text: "أهلًا بك 👋\nاسألني عن تخصصات جامعة جدة، القبول، الرسوم، المسارات، أو أي استفسار جامعي.",
    sender: "ai",
    timestamp: new Date().toLocaleTimeString(),
  });

  const [messages, setMessages] = useState([createWelcomeMessage()]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [chatHistory, setChatHistory] = useState(() => {
    const saved = localStorage.getItem("uniguide_chat_history");
    return saved ? JSON.parse(saved) : [];
  });

  const [currentChatId, setCurrentChatId] = useState(null);
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    "ما هي شروط القبول؟",
    "كم رسوم السنة التأهيلية؟",
    "ما هو المسار الصحي؟",
    "هل يوجد دبلومات؟",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const saveChatToHistory = (chatId, chatMessages, title) => {
    const saved = localStorage.getItem("uniguide_chat_history");
    const history = saved ? JSON.parse(saved) : [];

    const existingIndex = history.findIndex((chat) => chat.id === chatId);

    const chatData = {
      id: chatId,
      title: title || "محادثة جديدة",
      messages: chatMessages,
      createdAt: new Date().toISOString(),
    };

    let updatedHistory;

    if (existingIndex !== -1) {
      updatedHistory = [...history];
      updatedHistory[existingIndex] = chatData;
    } else {
      updatedHistory = [chatData, ...history];
    }

    setChatHistory(updatedHistory);
    localStorage.setItem("uniguide_chat_history", JSON.stringify(updatedHistory));
  };

  const handleNewChat = () => {
    setCurrentChatId(null);
    setMessages([createWelcomeMessage()]);
    setInputValue("");
  };

  const handleLoadChat = (chatId) => {
    const chat = chatHistory.find((item) => item.id === chatId);

    if (chat) {
      setCurrentChatId(chat.id);
      setMessages(chat.messages);
      setInputValue("");
    }
  };

  const handleQuickQuestion = (question) => {
    setInputValue(question);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (inputValue.trim() === "" || isLoading) return;

    const currentQuestion = inputValue.trim();

    const userMessage = {
      id: Date.now(),
      text: currentQuestion,
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
    };

    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInputValue("");
    setIsLoading(true);

    const chatId = currentChatId || Date.now();

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      });

      const data = await response.json();

      const aiMessage = {
        id: Date.now() + 1,
        text: data.answer || "لم أتمكن من توليد إجابة.",
        sender: "ai",
        timestamp: new Date().toLocaleTimeString(),
      };

      const finalMessages = [...updatedMessages, aiMessage];

      setMessages(finalMessages);
      setCurrentChatId(chatId);

      saveChatToHistory(
        chatId,
        finalMessages,
        currentQuestion.length > 35
          ? currentQuestion.slice(0, 35) + "..."
          : currentQuestion
      );
    } catch (error) {
      console.error("Backend error:", error);

      const errorMessage = {
        id: Date.now() + 1,
        text: "خدمة UniGuide AI غير متوفرة حالياً. تأكدي أن Backend شغال.",
        sender: "ai",
        timestamp: new Date().toLocaleTimeString(),
      };

      const finalMessages = [...updatedMessages, errorMessage];

      setMessages(finalMessages);
      setCurrentChatId(chatId);
      saveChatToHistory(chatId, finalMessages, currentQuestion);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA] flex text-[#003B70]" dir="rtl">
      <Sidebar
        onNewChat={handleNewChat}
        chatHistory={chatHistory}
        onLoadChat={handleLoadChat}
      />

      

      <main className="flex-1 flex flex-col mr-80 items-center">
        <section className="w-full max-w-5xl flex-1 flex flex-col items-center justify-center px-10 text-center pb-56">
          {messages.length <= 1 && (
            <>
              <h1 className="text-6xl font-bold mb-5 leading-tight">
                <span className="text-[#003B70]">مرحبًا،</span>{" "}
                <span>{user.name}</span>
              </h1>

              <p className="text-gray-500 text-3xl mb-10">
                كيف أقدر أساعدك اليوم؟
              </p>

              <div className="flex flex-wrap justify-center gap-4 max-w-4xl mb-12">
                {quickQuestions.map((q, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickQuestion(q)}
                    className="px-7 py-4 rounded-2xl border border-[#003B70] bg-white hover:bg-[#003B70] hover:text-white transition text-lg shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </>
          )}

          <div className="w-full max-w-3xl space-y-5 flex flex-col items-center">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`w-full flex ${
                  message.sender === "user" ? "justify-start" : "justify-center"
                }`}
              >
                <div
                  className={`max-w-3xl px-7 py-5 rounded-3xl shadow-sm leading-9 whitespace-pre-wrap text-right text-lg ${
                    message.sender === "user"
                      ? "bg-[#003B70] text-white"
                      : "bg-white border border-gray-200 text-[#1F2937]"
                  }`}
                >
                  <p>{message.text}</p>

                  <span
                    className={`text-xs mt-3 block ${
                      message.sender === "user" ? "text-white/70" : "text-gray-400"
                    }`}
                  >
                    {message.timestamp}
                  </span>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-center w-full">
                <div className="bg-white border border-gray-200 rounded-3xl px-6 py-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-[#003B70] rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-[#003B70] rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-[#003B70] rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </section>

        <div className="fixed bottom-6 left-[42%] -translate-x-1/2 w-[55%] max-w-4xl">
          <div className="bg-white border border-gray-200 rounded-full shadow-xl px-5 py-4">
            <form onSubmit={handleSendMessage} className="flex items-center gap-4">
              <button
                type="submit"
                disabled={isLoading}
                className="w-14 h-14 rounded-full bg-[#003B70] text-white flex items-center justify-center hover:bg-[#002855] transition disabled:opacity-40 text-xl"
              >
                ➤
              </button>

              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="اسأل عن القبول، التخصصات، المسارات..."
                disabled={isLoading}
                className="flex-1 bg-transparent outline-none text-xl placeholder:text-gray-400"
              />
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}