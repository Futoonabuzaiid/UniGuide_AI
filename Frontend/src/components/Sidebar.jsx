import { Plus, History, MessageCircle } from "lucide-react";
import ujLogo from "../assets/uj-logo.png";

export default function Sidebar({
  onNewChat,
  chatHistory = [],
  onLoadChat,
}) {
  return (
    <aside
      className="fixed top-0 right-0 h-screen w-80 bg-white border-l border-gray-200 z-50"
      dir="rtl"
    >
      <div className="px-6 pt-8 space-y-6 text-right">

        {/* University Logo + Title */}
        <div className="flex flex-col items-center mb-8">

          <img
            src={ujLogo}
            alt="University of Jeddah"
            className="w-24 h-24 object-contain mb-3"
          />

          <h2 className="font-bold text-[#003B70] text-3xl">
            UniGuide AI
          </h2>

          <p className="text-gray-500 text-sm mt-1">
            University of Jeddah
          </p>

        </div>

        {/* New Chat Button */}
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-between bg-[#003B70] text-white px-5 py-4 rounded-2xl hover:bg-[#002855] transition"
        >
          <span className="font-medium">محادثة جديدة</span>

          <Plus size={20} />
        </button>

        {/* Chat History */}
        <div>

          <div className="flex items-center justify-between mb-4 text-gray-500">
            <span className="font-semibold text-lg">
              المحادثات السابقة
            </span>

            <History size={18} />
          </div>

          <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">

            {chatHistory.length === 0 ? (
              <p className="text-sm text-gray-400 text-center mt-10">
                لا توجد محادثات سابقة
              </p>
            ) : (
              chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => onLoadChat(chat.id)}
                  className="w-full flex items-center gap-3 text-right px-4 py-4 rounded-2xl hover:bg-gray-100 text-sm transition"
                >
                  <MessageCircle
                    size={18}
                    className="text-[#003B70] shrink-0"
                  />

                  <span className="truncate text-gray-700">
                    {chat.title || "محادثة بدون عنوان"}
                  </span>

                </button>
              ))
            )}

          </div>
        </div>
      </div>
    </aside>
  );
}