// const IranAirChat=()=>{
// return(
//     <>
//     <div class="manualsContainer">
  

//       <h4 class="testReport">Report your issue</h4>
//       <label>write the issue for manager and get answer ASAP</label>
//       <form>
//         <textarea
          
          
//           placeholder="please write the problem"
//           required
//         ></textarea>
//         <button
          
//           class="submitIssueButton"
//           onClick={()=>{alert('your message submitted successfully , wait for the response.')}}
//         >
//           submit
//         </button>
//       </form>

//       <h2 class="mt-3 mb-1">output :</h2>
//       <pre>— nothing is there yet —</pre>
//     </div>
//     </>
// )

// }


// export default IranAirChat
// import React, { useEffect, useState } from "react";
// import { listMessages, sendMessage } from "../services/apiService";

// const IranAirChat = () => {
//   const [messageText, setMessageText] = useState("");
//   const [box, setBox] = useState("inbox");
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [sending, setSending] = useState(false);
//   const [status, setStatus] = useState("");

//   const fetchMessages = async () => {
//     setLoading(true);
//     setStatus("");

//     try {
//       const data = await listMessages({
//         box,
//         page: 1,
//         limit: 20,
//       });

//       const items =
//         data?.items ||
//         data?.results ||
//         data?.data ||
//         data?.messages ||
//         [];

//       setMessages(items);
//     } catch (error) {
//       console.error("Failed to load messages:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           "Failed to load messages."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchMessages();
//   }, [box]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     if (!messageText.trim()) return;

//     setSending(true);
//     setStatus("");

//     try {
//       // payload حداقلی
//       await sendMessage({
//         subject: "Issue Report",
//         body: messageText,
//       });

//       setStatus("Your message submitted successfully. Wait for the response.");
//       setMessageText("");
//       setBox("sent");
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to send message:", error);

//       const errorMessage =
//         error?.response?.data?.detail ||
//         JSON.stringify(error?.response?.data) ||
//         "Failed to send message.";

//       setStatus(errorMessage);
//     } finally {
//       setSending(false);
//     }
//   };

//   return (
//     <div className="manualsContainer">
//       <h4 className="testReport">Report your issue</h4>
//       <label>Write the issue for manager and get answer ASAP</label>

//       <form onSubmit={handleSubmit}>
//         <textarea
//           value={messageText}
//           onChange={(e) => setMessageText(e.target.value)}
//           placeholder="please write the problem"
//           required
//         />

//         <button
//           type="submit"
//           className="submitIssueButton"
//           disabled={sending}
//         >
//           {sending ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {status && <p style={{ marginTop: "10px" }}>{status}</p>}

//       <div style={{ marginTop: "20px" }}>
//         <label style={{ marginRight: "10px" }}>Message Box:</label>
//         <select value={box} onChange={(e) => setBox(e.target.value)}>
//           <option value="inbox">Inbox</option>
//           <option value="sent">Sent</option>
//           <option value="all">All</option>
//         </select>

//         <button
//           type="button"
//           onClick={fetchMessages}
//           style={{ marginLeft: "10px" }}
//         >
//           Refresh
//         </button>
//       </div>

      

//       {loading ? (
//         <pre>Loading messages...</pre>
//       ) : messages.length === 0 ? (
//         <pre>— nothing is there yet —</pre>
//       ) : (
//         <div style={{ marginTop: "10px" }}>
//           {messages.map((msg) => (
//             <div
//               key={msg.id || `${msg.subject}-${msg.created_at}`}
//               style={{
//                 border: "1px solid #ddd",
//                 borderRadius: "8px",
//                 padding: "12px",
//                 marginBottom: "10px",
//                 background: "#fff",
//               }}
//             >
//               <strong>{msg.subject || "No Subject"}</strong>
//               <p style={{ margin: "8px 0" }}>
//                 {msg.body || msg.content || "No message body"}
//               </p>
//               <small style={{ color: "#777" }}>
//                 {msg.created_at || msg.createdAt || ""}
//               </small>
//             </div>
//           ))}
//         </div>
//       )}
//     </div>
//   );
// };

// export default IranAirChat;


// import React, { useEffect, useState } from "react";
// import {
//   listMessages,
//   sendMessage,
//   markMessageAsRead,
// } from "../services/apiService";

// const IranAirChat = () => {
//   const [messageText, setMessageText] = useState("");
//   const [box, setBox] = useState("inbox");
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [sending, setSending] = useState(false);
//   const [status, setStatus] = useState("");

//   const fetchMessages = async () => {
//     setLoading(true);
//     setStatus("");

//     try {
//       const data = await listMessages({
//         box,
//         page: 1,
//         limit: 20,
//       });

//       const items =
//         data?.items ||
//         data?.results ||
//         data?.data ||
//         data?.messages ||
//         [];

//       setMessages(items);
//     } catch (error) {
//       console.error("Failed to load messages:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           "Failed to load messages."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchMessages();
//   }, [box]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     if (!messageText.trim()) return;

//     setSending(true);
//     setStatus("");

//     try {
//       await sendMessage({
//         subject: "Issue Report",
//         body: messageText,
//       });

//       setStatus("Your message submitted successfully. Wait for the response.");
//       setMessageText("");
//       setBox("sent");
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to send message:", error);

//       const errorMessage =
//         error?.response?.data?.detail ||
//         JSON.stringify(error?.response?.data) ||
//         "Failed to send message.";

//       setStatus(errorMessage);
//     } finally {
//       setSending(false);
//     }
//   };

//   const handleMarkAsRead = async (messageId) => {
//     if (!messageId) return;

//     try {
//       await markMessageAsRead(messageId);
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to mark message as read:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           "Failed to mark message as read."
//       );
//     }
//   };

//   return (
//     <div className="manualsContainer">
//       <h4 className="testReport">Report your issue</h4>
//       <label>Write the issue for manager and get answer ASAP</label>

//       <form onSubmit={handleSubmit}>
//         <textarea
//           value={messageText}
//           onChange={(e) => setMessageText(e.target.value)}
//           placeholder="please write the problem"
//           required
//         />

//         <button
//           type="submit"
//           className="submitIssueButton"
//           disabled={sending}
//         >
//           {sending ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {status && <p style={{ marginTop: "10px" }}>{status}</p>}

//       <div style={{ marginTop: "20px" }}>
//         <label style={{ marginRight: "10px" }}>Message Box:</label>
//         <select value={box} onChange={(e) => setBox(e.target.value)}>
//           <option value="inbox">Inbox</option>
//           <option value="sent">Sent</option>
//           <option value="all">All</option>
//         </select>

//         <button
//           type="button"
//           onClick={fetchMessages}
//           style={{ marginLeft: "10px" }}
//         >
//           Refresh
//         </button>
//       </div>

      

//       {loading ? (
//         <pre>Loading messages...</pre>
//       ) : messages.length === 0 ? (
//         <pre>— nothing is there yet —</pre>
//       ) : (
//         <div style={{ marginTop: "10px" }}>
//           {messages.map((msg) => (
//             <div
//               key={msg.id || `${msg.subject}-${msg.created_at}`}
//               onClick={() => handleMarkAsRead(msg.id)}
//               style={{
//                 border: "1px solid #ddd",
//                 borderRadius: "8px",
//                 padding: "12px",
//                 marginBottom: "10px",
//                 background: msg.is_read ? "#fff" : "#f5f9ff",
//                 cursor: "pointer",
//               }}
//             >
//               <strong>
//                 {msg.subject || "No Subject"} {!msg.is_read && "• unread"}
//               </strong>

//               <p style={{ margin: "8px 0" }}>
//                 {msg.body || msg.content || "No message body"}
//               </p>

//               <small style={{ color: "#777" }}>
//                 {msg.created_at || msg.createdAt || ""}
//               </small>
//             </div>
//           ))}
//         </div>
//       )}
//     </div>
//   );
// };

// export default IranAirChat;

// import React, { useEffect, useMemo, useState } from "react";
// import {
//   listMessages,
//   sendMessage,
//   markMessageAsRead,
//   getCurrentUser,
// } from "../services/apiService";

// const IranAirChat = () => {
//   const [messageText, setMessageText] = useState("");
//   const [box, setBox] = useState("inbox");
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [sending, setSending] = useState(false);
//   const [status, setStatus] = useState("");
//   const [currentUser, setCurrentUser] = useState(null);
//   const [recipientIds, setRecipientIds] = useState(""); // فقط برای admin

//   const role = currentUser?.role;

//   const isAdmin = useMemo(() => role === "admin", [role]);
//   const isPilotOrChief = useMemo(
//     () => role === "pilot" || role === "chief_pilot",
//     [role]
//   );

//   useEffect(() => {
//     const loadCurrentUser = async () => {
//       try {
//         const me = await getCurrentUser();
//         setCurrentUser(me);
//       } catch (error) {
//         console.error("Failed to load current user:", error);
//       }
//     };

//     loadCurrentUser();
//   }, []);

//   const fetchMessages = async () => {
//     setLoading(true);
//     setStatus("");

//     try {
//       const data = await listMessages({
//         box,
//         page: 1,
//         limit: 20,
//       });

//       const items =
//         data?.items ||
//         data?.results ||
//         data?.data ||
//         data?.messages ||
//         [];

//       setMessages(items);
//     } catch (error) {
//       console.error("Failed to load messages:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           "Failed to load messages."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchMessages();
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, [box]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const trimmedMessage = messageText.trim();
//     if (!trimmedMessage) return;

//     if (!currentUser) {
//       setStatus("Loading user info...");
//       return;
//     }

//     setSending(true);
//     setStatus("");

//     try {
//       const payload = {
//         subject: "Issue Report",
//         body: trimmedMessage,
//       };

//       if (isAdmin) {
//         const ids = recipientIds
//           .split(",")
//           .map((id) => Number(id.trim()))
//           .filter((id) => Number.isInteger(id) && id > 0);

//         if (!ids.length) {
//           setStatus("For admin users, at least one recipient_id is required.");
//           return;
//         }

//         payload.recipient_ids = ids;
//       }

//       // برای pilot / chief_pilot نباید recipient_ids ارسال شود
//       await sendMessage(payload);

//       setStatus("Your message submitted successfully. Wait for the response.");
//       setMessageText("");
//       if (isAdmin) setRecipientIds("");
//       setBox("sent");
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to send message:", error);

//       const errorMessage =
//         error?.response?.data?.detail ||
//         error?.response?.data?.error ||
//         JSON.stringify(error?.response?.data) ||
//         "Failed to send message.";

//       setStatus(errorMessage);
//     } finally {
//       setSending(false);
//     }
//   };

//   const handleMarkAsRead = async (messageId) => {
//     if (!messageId) return;

//     try {
//       await markMessageAsRead(messageId);
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to mark message as read:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           "Failed to mark message as read."
//       );
//     }
//   };

//   return (
//     <div className="manualsContainer">
//       <h4 className="testReport">Report your issue</h4>

//       <label>Write the issue for manager and get answer ASAP</label>

//       {currentUser && (
//         <p style={{ marginTop: "8px", color: "#666", fontSize: "12px" }}>
//           Current role: <strong>{currentUser.role}</strong>
//         </p>
//       )}

//       <form onSubmit={handleSubmit}>
//         <textarea
//           value={messageText}
//           onChange={(e) => setMessageText(e.target.value)}
//           placeholder="please write the problem"
//           required
//         />

//         {isAdmin && (
//           <div style={{ marginTop: "12px" }}>
//             <label style={{ display: "block", marginBottom: "6px" }}>
//               Recipient IDs (comma-separated)
//             </label>
//             <input
//               type="text"
//               value={recipientIds}
//               onChange={(e) => setRecipientIds(e.target.value)}
//               placeholder="e.g. 12, 18, 24"
//               style={{
//                 width: "100%",
//                 padding: "10px",
//                 border: "1px solid #ccc",
//                 borderRadius: "6px",
//               }}
//             />
//             <small style={{ color: "#777" }}>
//               Required for admin users.
//             </small>
//           </div>
//         )}

//         <button
//           type="submit"
//           className="submitIssueButton"
//           disabled={sending}
//         >
//           {sending ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {status && <p style={{ marginTop: "10px" }}>{status}</p>}

//       <div style={{ marginTop: "20px" }}>
//         <label style={{ marginRight: "10px" }}>Message Box:</label>
//         <select value={box} onChange={(e) => setBox(e.target.value)}>
//           <option value="inbox">Inbox</option>
//           <option value="sent">Sent</option>
//           <option value="all">All</option>
//         </select>

//         <button
//           type="button"
//           onClick={fetchMessages}
//           style={{ marginLeft: "10px" }}
//         >
//           Refresh
//         </button>
//       </div>

//       {loading ? (
//         <pre>Loading messages...</pre>
//       ) : messages.length === 0 ? (
//         <pre>— nothing is there yet —</pre>
//       ) : (
//         <div style={{ marginTop: "10px" }}>
//           {messages.map((msg) => {
//             const isRead = Boolean(msg.is_read || msg.read_at);
//             return (
//               <div
//                 key={msg.id || `${msg.subject}-${msg.created_at}`}
//                 onClick={() => !isRead && handleMarkAsRead(msg.id)}
//                 style={{
//                   border: "1px solid #ddd",
//                   borderRadius: "8px",
//                   padding: "12px",
//                   marginBottom: "10px",
//                   background: isRead ? "#fff" : "#f5f9ff",
//                   cursor: isRead ? "default" : "pointer",
//                 }}
//               >
//                 <strong>
//                   {msg.subject || "No Subject"} {!isRead && "• unread"}
//                 </strong>

//                 <p style={{ margin: "8px 0" }}>
//                   {msg.body || msg.content || "No message body"}
//                 </p>

//                 <small style={{ color: "#777" }}>
//                   {msg.created_at || msg.createdAt || ""}
//                 </small>
//               </div>
//             );
//           })}
//         </div>
//       )}
//     </div>
//   );
// };

// export default IranAirChat;

// import React, { useEffect, useMemo, useState } from "react";
// import {
//   listMessages,
//   sendMessage,
//   markMessageAsRead,
//   getCurrentUser,
// } from "../services/apiService";

// const IranAirChat = () => {
//   const [messageText, setMessageText] = useState("");
//   const [box, setBox] = useState("inbox");
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [sending, setSending] = useState(false);
//   const [status, setStatus] = useState("");
//   const [currentUser, setCurrentUser] = useState(null);
//   const [recipientIds, setRecipientIds] = useState("");

//   const role = currentUser?.role;

//   const isAdmin = useMemo(() => role === "admin", [role]);
//   const isPilotOrChief = useMemo(
//     () => role === "pilot" || role === "chief_pilot",
//     [role]
//   );

//   useEffect(() => {
//     const loadCurrentUser = async () => {
//       try {
//         const me = await getCurrentUser();
//         setCurrentUser(me);
//       } catch (error) {
//         console.error("Failed to load current user:", error);
//       }
//     };

//     loadCurrentUser();
//   }, []);

//   const fetchMessages = async () => {
//     setLoading(true);
//     setStatus("");

//     try {
//       const data = await listMessages({
//         box,
//         page: 1,
//         limit: 20,
//       });

//       const items =
//         data?.items ||
//         data?.results ||
//         data?.data ||
//         data?.messages ||
//         [];

//       setMessages(items);
//     } catch (error) {
//       console.error("Failed to load messages:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           "Failed to load messages."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchMessages();
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, [box]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const trimmedMessage = messageText.trim();
//     if (!trimmedMessage) return;

//     if (!currentUser) {
//       setStatus("Loading user info...");
//       return;
//     }

//     setSending(true);
//     setStatus("");

//     try {
//       const payload = {
//         subject: "Issue Report",
//         body: trimmedMessage,
//       };

//       if (isAdmin) {
//         const ids = recipientIds
//           .split(",")
//           .map((id) => Number(id.trim()))
//           .filter((id) => Number.isInteger(id) && id > 0);

//         if (!ids.length) {
//           setStatus("For admin users, at least one recipient_id is required.");
//           setSending(false);
//           return;
//         }

//         payload.recipient_ids = ids;
//       }

//       await sendMessage(payload);

//       setStatus("Your message submitted successfully. Wait for the response.");
//       setMessageText("");
//       if (isAdmin) setRecipientIds("");
//       setBox("sent");
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to send message:", error);

//       const errorMessage =
//         error?.response?.data?.detail ||
//         error?.response?.data?.error ||
//         JSON.stringify(error?.response?.data) ||
//         "Failed to send message.";

//       setStatus(errorMessage);
//     } finally {
//       setSending(false);
//     }
//   };

//   const handleMarkAsRead = async (messageId) => {
//     if (!messageId) return;

//     try {
//       await markMessageAsRead(messageId);
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to mark message as read:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           "Failed to mark message as read."
//       );
//     }
//   };

//   return (
//     <div className="manualsContainer chatbox" >
//       <h4 className="testReport">Report your issue</h4>

//       <label>Write the issue for manager and get answer ASAP</label>

//       {currentUser && (
//         <p style={{ marginTop: "8px", color: "#666", fontSize: "12px" }}>
//           Current role: <strong>{currentUser.role}</strong>
//         </p>
//       )}

//       <form onSubmit={handleSubmit}>
//         <textarea
//           value={messageText}
//           onChange={(e) => setMessageText(e.target.value)}
//           placeholder="please write the problem"
//           required
//         />

//         {isAdmin && (
//           <div style={{ marginTop: "12px" }} >
//             <label style={{ display: "block", marginBottom: "6px" }}>
//               Recipient IDs (comma-separated)
//             </label>
//             <input
//               type="text"
//               value={recipientIds}
//               onChange={(e) => setRecipientIds(e.target.value)}
//               placeholder="e.g. 12, 18, 24"
//               style={{
//                 width: "100%",
//                 padding: "10px",
//                 border: "1px solid #ccc",
//                 borderRadius: "6px",
//               }}
//             />
//             <small style={{ color: "#777" }}>
//               Required for admin users.
//             </small>
//           </div>
//         )}

//         <button
//           type="submit"
//           className="submitIssueButton"
//           disabled={sending}
//         >
//           {sending ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {status && <p style={{ marginTop: "10px" }}>{status}</p>}

//       <div style={{ marginTop: "20px" }}>
//         <label style={{ marginRight: "10px" }}>Message Box:</label>
//         <select value={box} onChange={(e) => setBox(e.target.value)}>
//           <option value="inbox">Inbox</option>
//           <option value="sent">Sent</option>
//           <option value="all">All</option>
//         </select>

//         <button
//           type="button"
//           onClick={fetchMessages}
//           style={{ marginLeft: "10px" }}
//         >
//           Refresh
//         </button>
//       </div>

//       {loading ? (
//         <pre>Loading messages...</pre>
//       ) : messages.length === 0 ? (
//         <pre>— nothing is there yet —</pre>
//       ) : (
//         <div style={{
//     marginTop: "10px",
//     maxHeight: "400px",
//     overflowY: "auto",
//     overflowX: "hidden",
//     paddingRight: "4px",
//   }}>
//           {messages.map((msg) => {
//             const isRead = Boolean(msg.is_read || msg.read_at);

//             const senderId = msg.sender_id ?? msg.sender?.id;
//             const senderName = msg.sender?.name || "Unknown";

//             const recipientId = msg.recipient_id ?? msg.recipient?.id;
//             const recipientName = msg.recipient?.name || "Unknown";

//             return (
//               <div
//                 key={msg.id || `${msg.subject}-${msg.created_at}`}
//                 onClick={() =>
//                   !isRead && box === "inbox" && handleMarkAsRead(msg.id)
//                 }
//                 style={{
//                   border: "1px solid #ddd",
//                   borderRadius: "8px",
//                   padding: "12px",
//                   marginBottom: "10px",
//                   background: isRead ? "#fff" : "#f5f9ff",
//                   cursor:
//                     !isRead && box === "inbox" ? "pointer" : "default",
//                 }}
//               >
//                 <div
//                   style={{
//                     display: "flex",
//                     justifyContent: "space-between",
//                     alignItems: "center",
//                     marginBottom: "8px",
//                   }}
//                 >
//                   <strong>
//                     #{msg.id} — {msg.subject || "No Subject"}{" "}
//                     {!isRead && "• unread"}
//                   </strong>

//                   <small style={{ color: "#777" }}>
//                     {msg.created_at
//                       ? new Date(msg.created_at).toLocaleString()
//                       : ""}
//                   </small>
//                 </div>

//                 <div style={{ marginBottom: "8px", fontSize: "12px", color: "#555" }}>
//                   <div>
//                     <strong>From:</strong> {senderName} (id: {senderId})
//                   </div>
//                   <div>
//                     <strong>To:</strong> {recipientName} (id: {recipientId})
//                   </div>
//                 </div>

//                 <p style={{ margin: "8px 0" }}>
//                   {msg.body || msg.content || "No message body"}
//                 </p>
//               </div>
//             );
//           })}
//         </div>
//       )}
//     </div>
//   );
// };

// export default IranAirChat;


// import React, { useEffect, useMemo, useState } from "react";

// import {
//   listMessages,
//   sendMessage,
//   markMessageAsRead,
//   getCurrentUser,
// } from "../services/apiService"; 
// import refreshIcon from '../assets/icons/icons8-refresh-500.svg';
// import riskicon from '../assets/icons/risk-icon.svg';
// const IranAirChat = () => {
//   const [messageText, setMessageText] = useState("");
//   const [box, setBox] = useState("inbox");
//   const [messages, setMessages] = useState([]);
//   const [subject, setSubject] = useState("");

//   const [loading, setLoading] = useState(false);
//   const [sending, setSending] = useState(false);
//   const [status, setStatus] = useState("");
//   const [currentUser, setCurrentUser] = useState(null);
//   const [recipientIds, setRecipientIds] = useState("");

//   const role = currentUser?.role;
//   const isAdmin = useMemo(() => role === "admin", [role]);

//   const loadCurrentUser = async () => {
//     try {
//       const me = await getCurrentUser();
//       setCurrentUser(me);
//     } catch (error) {
//       console.error("Failed to load current user:", error);
//       setStatus("Failed to load user information.");
//     }
//   };

//   const fetchMessages = async () => {
//     setLoading(true);
//     setStatus("");

//     try {
//       const data = await listMessages({
//         box,
//         page: 1,
//         limit: 20,
//       });

//       const items =
//         data?.items ||
//         data?.results ||
//         data?.data ||
//         data?.messages ||
//         [];

//       setMessages(items);
//     } catch (error) {
//       console.error("Failed to load messages:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           error.message ||
//           "Failed to load messages."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     loadCurrentUser();
//   }, []);

//   useEffect(() => {
//     fetchMessages();
    
//   }, [box]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const trimmedMessage = messageText.trim();
//     if (!trimmedMessage) return;

//     if (!currentUser) {
//       setStatus("Loading user info...");
//       return;
//     }

//     setSending(true);
//     setStatus("");

//     try {
//       const payload = {
//         subject : subject.trim(),
//         body: trimmedMessage,
//       };

//       if (isAdmin) {
//         const ids = recipientIds
//           .split(",")
//           .map((id) => Number(id.trim()))
//           .filter((id) => Number.isInteger(id) && id > 0);

//         if (!ids.length) {
//           setStatus("For admin users, at least one recipient_id is required.");
//           setSending(false); 
//           return;
//         }

//         payload.recipient_ids = ids;
//       }

//       await sendMessage(payload);

//       setStatus("Your message submitted successfully. Wait for the response.");
//       setMessageText("");
//       if (isAdmin) setRecipientIds("");
//       setBox("sent");
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to send message:", error);
//       const errorMessage =
//         error?.response?.data?.detail ||
//         error?.response?.data?.error ||
//         JSON.stringify(error?.response?.data) ||
//         error.message ||
//         "Failed to send message.";
//       setStatus(errorMessage);
//     } finally {
//       setSending(false);
//     }
//   };

//   const handleMarkAsRead = async (messageId) => {
//     if (!messageId) return;

//     try {
//       await markMessageAsRead(messageId);
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to mark message as read:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           error.message ||
//           "Failed to mark message as read."
//       );
//     }
//   };

//   return (
//     <div className="manualsContainer chatbox">
//       <h4 className="testReport">Report your issue</h4>

//       <label>Write the issue for manager and get answer ASAP</label>

//       {currentUser && (
//         <p className="chat-role">
//           Current role: <strong>{currentUser.role}</strong>
//         </p>
//       )}

//       <form onSubmit={handleSubmit}>
//         <input
//   type="text"
//   placeholder="Subject (optional)"
//   value={subject}
//   onChange={(e) => setSubject(e.target.value)}
//   className="chat-subject-input"
// />

//         <textarea
//           value={messageText}
//           onChange={(e) => setMessageText(e.target.value)}
//           placeholder="please write the problem"
//           required
//         />

//         {isAdmin && (
//           <div className="chat-recipient-box">
//             <label className="chat-recipient-label">
//               Recipient IDs (comma-separated)
//             </label>
//             <input
//               type="text"
//               value={recipientIds}
//               onChange={(e) => setRecipientIds(e.target.value)}
//               placeholder="e.g. 12, 18, 24"
//               className="chat-recipient-input"
//             />
//             <small className="chat-recipient-help">
//               Required for admin users.
//             </small>
//           </div>
//         )}

//         <button
//           type="submit"
//           className="submitIssueButton"
//           disabled={sending}
//         >
//           {sending ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {status && <p className="chat-status">{status}</p>}

//       <div className="chat-toolbar">
//         <label className="chat-toolbar-label">Message Box:</label>
//         <select value={box} onChange={(e) => setBox(e.target.value)}>
//           <option value="inbox">Inbox</option>
//           <option value="sent">Sent</option>
//           <option value="all">All</option>
//         </select>

//         <button
//           type="button"
//           onClick={fetchMessages}
//           className="chat-refresh-btn"
//         >
//           <img src={refreshIcon} style={{width:'24px '}} alt="" />
//         </button>
//       </div>

//       {loading ? (
//         <pre>Loading messages...</pre>
//       ) : messages.length === 0 ? (
//         <pre>— nothing is there yet —</pre>
//       ) : (
//         <div className="chat-messages">
//           {messages.map((msg) => {
//             const isRead = Boolean(msg.is_read || msg.read_at);

//             const senderId = msg.sender_id ?? msg.sender?.id;
//             const senderName = msg.sender?.name || "Unknown";

//             const recipientId = msg.recipient_id ?? msg.recipient?.id;
//             const recipientName = msg.recipient?.name || "Unknown";

//             return (
//               <div
//                 key={msg.id || `${msg.subject}-${msg.created_at}`}
//                 onClick={() =>
//                   !isRead && box === "inbox" && handleMarkAsRead(msg.id)
//                 }
//                 className={`chat-message-card ${
//                   !isRead && box === "inbox" ? "unread" : ""
//                 }`}
//               >
//                 <div className="chat-message-header">
//                   <strong className="chat-message-title">
//                     #{msg.id} — {msg.subject || "No Subject"}{" "}
//                     {!isRead && <img src={riskicon} alt="" />}
//                   </strong>

//                   <small className="chat-message-date">
//                     {msg.created_at
//                       ? new Date(msg.created_at).toLocaleString()
//                       : ""}
//                   </small>
//                 </div>

//                 <div className="chat-message-meta">
//                   <div>
//                     <strong>From:</strong> {senderName} (id: {senderId})
//                   </div>
//                   <div>
//                     <strong>To:</strong> {recipientName} (id: {recipientId})
//                   </div>
//                 </div>

//                 <p className="chat-message-body">
//                   {msg.body || msg.content || "No message body"}
//                 </p>
//               </div>
//             );
//           })}
//         </div>
//       )}
//     </div>
//   );
// };

// export default IranAirChat;

// import React, { useEffect, useMemo, useRef, useState } from "react";
// import {
//   listMessages,
//   sendMessage,
//   markMessageAsRead,
//   getCurrentUser,
// } from "../services/apiService";
// import refreshIcon from "../assets/icons/icons8-refresh-500.svg";
// import riskicon from "../assets/icons/risk-icon.svg";

// const IranAirChat = () => {
//   const [messageText, setMessageText] = useState("");
//   const [box, setBox] = useState("inbox");
//   const [messages, setMessages] = useState([]);
//   const [subject, setSubject] = useState("");
//   const [replyTo, setReplyTo] = useState(null);

//   const [loading, setLoading] = useState(false);
//   const [sending, setSending] = useState(false);
//   const [status, setStatus] = useState("");
//   const [currentUser, setCurrentUser] = useState(null);
//   const [recipientIds, setRecipientIds] = useState("");
// const [activeTab, setActiveTab] = useState("submit");

//   const formRef = useRef(null);

//   const role = currentUser?.role;
//   const isAdmin = useMemo(() => role === "admin", [role]);

//   const loadCurrentUser = async () => {
//     try {
//       const me = await getCurrentUser();
//       setCurrentUser(me);
//     } catch (error) {
//       console.error("Failed to load current user:", error);
//       setStatus("Failed to load user information.");
//     }
//   };

//   const fetchMessages = async () => {
//     setLoading(true);
//     setStatus("");

//     try {
//       const data = await listMessages({
//         box,
//         page: 1,
//         limit: 20,
//       });

//       const items =
//         data?.items ||
//         data?.results ||
//         data?.data ||
//         data?.messages ||
//         [];

//       setMessages(items);
//     } catch (error) {
//       console.error("Failed to load messages:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           error.message ||
//           "Failed to load messages."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     loadCurrentUser();
//   }, []);

//   useEffect(() => {
//     fetchMessages();
//   }, [box]);

//   const handleReply = (msg) => {
//     const senderId = msg.sender_id ?? msg.sender?.id;
//     const originalSubject = msg.subject?.trim();

//     if (!subject.trim()) {
//       setSubject(originalSubject ? `Re: ${originalSubject}` : "Re:");
//     }

//     // برای admin می‌توانی دستی recipient را تغییر بدهی
//     // برای کاربر معمولی/پایلوت اگر لازم بود گیرنده را روی فرستنده قبلی بگذار
//     if (senderId) {
//       setRecipientIds(String(senderId));
//     }

//     setReplyTo(msg);

//     formRef.current?.scrollIntoView({
//       behavior: "smooth",
//       block: "start",
//     });
//   };

//   const clearReply = () => {
//     setReplyTo(null);
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const trimmedMessage = messageText.trim();
//     if (!trimmedMessage) return;

//     if (!currentUser) {
//       setStatus("Loading user info...");
//       return;
//     }

//     setSending(true);
//     setStatus("");

//     try {
//       const payload = {
//         subject: subject.trim(),
//         body: trimmedMessage,
//       };

//       // اگر بک‌اند reply واقعی پشتیبانی می‌کند این را فعال کن:
//       // if (replyTo?.id) {
//       //   payload.reply_to_message_id = replyTo.id;
//       // }

//       if (isAdmin) {
//         const ids = recipientIds
//           .split(",")
//           .map((id) => Number(id.trim()))
//           .filter((id) => Number.isInteger(id) && id > 0);

//         if (!ids.length) {
//           setStatus("For admin users, at least one recipient_id is required.");
//           setSending(false);
//           return;
//         }

//         payload.recipient_ids = ids;
//       }

//       await sendMessage(payload);

//       setStatus("Your message submitted successfully. Wait for the response.");
//       setMessageText("");
//       setSubject("");
//       if (isAdmin) setRecipientIds("");
//       setReplyTo(null);
//       setBox("sent");
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to send message:", error);
//       const errorMessage =
//         error?.response?.data?.detail ||
//         error?.response?.data?.error ||
//         JSON.stringify(error?.response?.data) ||
//         error.message ||
//         "Failed to send message.";
//       setStatus(errorMessage);
//     } finally {
//       setSending(false);
//     }
//   };

//   const handleMarkAsRead = async (messageId) => {
//     if (!messageId) return;

//     try {
//       await markMessageAsRead(messageId);
//       await fetchMessages();
//     } catch (error) {
//       console.error("Failed to mark message as read:", error);
//       setStatus(
//         error?.response?.data?.detail ||
//           error?.response?.data?.error ||
//           error.message ||
//           "Failed to mark message as read."
//       );
//     }
//   };

//   return (
//     <div className="manualsContainer chatbox">
//       <h4 className="testReport">Report your issue</h4>
//       <label>Write the issue for manager and get answer ASAP</label>

//       {currentUser && (
//         <p className="chat-role">
//           Current role: <strong>{currentUser.role}</strong>
//         </p>
//       )}

//       <form onSubmit={handleSubmit} ref={formRef}>
//         {replyTo && (
//           <div className="chat-reply-banner">
//             <div>
//               Replying to message <strong>#{replyTo.id}</strong>
//               {replyTo.subject ? <> — {replyTo.subject}</> : null}
//             </div>
//             <button
//               type="button"
//               className="chat-cancel-reply-btn"
//               onClick={clearReply}
//             >
//               Cancel reply
//             </button>
//           </div>
//         )}

//         <input
//           type="text"
//           placeholder="Subject (optional)"
//           value={subject}
//           onChange={(e) => setSubject(e.target.value)}
//           className="chat-subject-input"
//         />

//         <textarea
//           value={messageText}
//           onChange={(e) => setMessageText(e.target.value)}
//           placeholder="please write the problem"
//           required
//         />

//         {isAdmin && (
//           <div className="chat-recipient-box">
//             <label className="chat-recipient-label">
//               Recipient IDs (comma-separated)
//             </label>
//             <input
//               type="text"
//               value={recipientIds}
//               onChange={(e) => setRecipientIds(e.target.value)}
//               placeholder="e.g. 12, 18, 24"
//               className="chat-recipient-input"
//             />
//             <small className="chat-recipient-help">
//               Required for admin users.
//             </small>
//           </div>
//         )}

//         <button
//           type="submit"
//           className="submitIssueButton"
//           disabled={sending}
//         >
//           {sending ? "Submitting..." : replyTo ? "Send Reply" : "Submit"}
//         </button>
//       </form>

//       {status && <p className="chat-status">{status}</p>}

//       <div className="chat-toolbar">
//         <label className="chat-toolbar-label">Message Box:</label>
//         <select value={box} onChange={(e) => setBox(e.target.value)}>
//           <option value="inbox">Inbox</option>
//           <option value="sent">Sent</option>
//           <option value="all">All</option>
//         </select>

//         <button
//           type="button"
//           onClick={fetchMessages}
//           className="chat-refresh-btn"
//           title="Refresh"
//         >
//           <img src={refreshIcon} style={{ width: "24px" }} alt="refresh" />
//         </button>
//       </div>

//       {loading ? (
//         <pre>Loading messages...</pre>
//       ) : messages.length === 0 ? (
//         <pre>— nothing is there yet —</pre>
//       ) : (
//         <div className="chat-messages">
//           {messages.map((msg) => {
//             const isRead = Boolean(msg.is_read || msg.read_at);

//             const senderId = msg.sender_id ?? msg.sender?.id;
//             const senderName = msg.sender?.name || "Unknown";

//             const recipientId = msg.recipient_id ?? msg.recipient?.id;
//             const recipientName = msg.recipient?.name || "Unknown";

//             return (
//               <div
//                 key={msg.id || `${msg.subject}-${msg.created_at}`}
//                 onClick={() =>
//                   !isRead && box === "inbox" && handleMarkAsRead(msg.id)
//                 }
//                 className={`chat-message-card ${
//                   !isRead && box === "inbox" ? "unread" : ""
//                 }`}
//               >
//                 <div className="chat-message-header">
//                   <strong className="chat-message-title">
//                     #{msg.id} — {msg.subject || "No Subject"}
//                     {!isRead && box === "inbox" && (
//                       <img
//                         src={riskicon}
//                         alt="unread"
//                         className="chat-unread-icon"
//                       />
//                     )}
//                   </strong>

//                   <small className="chat-message-date">
//                     {msg.created_at
//                       ? new Date(msg.created_at).toLocaleString()
//                       : ""}
//                   </small>
//                 </div>

//                 <div className="chat-message-actions">
//                   <button
//                     type="button"
//                     className="chat-reply-btn"
//                     onClick={(e) => {
//                       e.stopPropagation();
//                       handleReply(msg);
//                     }}
//                   >
//                     Reply
//                   </button>
//                 </div>

//                 <div className="chat-message-meta">
//                   <div>
//                     <strong>From:</strong> {senderName} (id: {senderId})
//                   </div>
//                   <div>
//                     <strong>To:</strong> {recipientName} (id: {recipientId})
//                   </div>
//                 </div>

//                 <p className="chat-message-body">
//                   {msg.body || msg.content || "No message body"}
//                 </p>
//               </div>
//             );
//           })}
//         </div>
//       )}
//     </div>
//   );
// };

// export default IranAirChat;

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  listMessages,
  sendMessage,
 markMessageAsRead,
  getCurrentUser,
} from "../services/apiService";
import refreshIcon from "../assets/icons/icons8-refresh-500.svg";
import riskicon from "../assets/icons/risk-icon.svg";
import PageWrapper from "../components/PageWrapper";

const IranAirChat = () => {
  const [activeTab, setActiveTab] = useState("submit");

  const [messageText, setMessageText] = useState("");
  const [box, setBox] = useState("inbox");
  const [messages, setMessages] = useState([]);
  const [subject, setSubject] = useState("");
  const [replyTo, setReplyTo] = useState(null);


  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [status, setStatus] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [recipientIds, setRecipientIds] = useState("");


  const formRef = useRef(null);


  const role = currentUser?.role;
  const isAdmin = useMemo(() => role === "admin", [role]);

  const loadCurrentUser = async () => {
    try {
      const me = await getCurrentUser();
      setCurrentUser(me);
    } catch (error) {
      console.error("Failed to load current user:", error);
      setStatus("Failed to load user information.");
    }
  };

  const fetchMessages = async () => {
    setLoading(true);
    setStatus("");

    try {
      const data = await listMessages({
        box,
        page: 1,
        limit: 20,
      });

      const items =
        data?.items ||
        data?.results ||
        data?.data ||
        data?.messages ||
        [];

      setMessages(items);
    } catch (error) {
      console.error("Failed to load messages:", error);
      setStatus(
        error?.response?.data?.detail ||
          error?.response?.data?.error ||
          error.message ||
          "Failed to load messages."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCurrentUser();
  }, []);

  useEffect(() => {

    if (activeTab === "messages") {
      fetchMessages();
    }
  }, [box, activeTab]);

  const handleReply = (msg) => {
    const senderId = msg.sender_id ?? msg.sender?.id;
    const originalSubject = msg.subject?.trim();

    setActiveTab("submit");

    if (!subject.trim()) {
      setSubject(originalSubject ? `Re: ${originalSubject}` : "Re:");
    }

    if (senderId) {
      setRecipientIds(String(senderId));
    }

    setReplyTo(msg);

    setTimeout(() => {
      formRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 50);
  };

  const clearReply = () => {
    setReplyTo(null);
  };


  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedMessage = messageText.trim();
    if (!trimmedMessage) return;

    if (!currentUser) {
      setStatus("Loading user info...");
      return;
    }

    setSending(true);
    setStatus("");

    try {
      const payload = {

        subject: subject.trim(),
        body: trimmedMessage,
      };

      


      if (isAdmin) {
        const ids = recipientIds
          .split(",")
          .map((id) => Number(id.trim()))
          .filter((id) => Number.isInteger(id) && id > 0);

        if (!ids.length) {
          setStatus("For admin users, at least one recipient_id is required.");

          setSending(false);

          return;
        }

        payload.recipient_ids = ids;
      }

      await sendMessage(payload);

      setStatus("Your message submitted successfully. Wait for the response.");
      setMessageText("");

      setSubject("");
      if (isAdmin) setRecipientIds("");
      setReplyTo(null);

      setActiveTab("messages");
      setBox("sent");
      await fetchMessages();
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.error ||
        JSON.stringify(error?.response?.data) ||
        error.message ||
        "Failed to send message.";
      setStatus(errorMessage);
    } finally {
      setSending(false);
    }
  };

  const handleMarkAsRead = async (messageId) => {
    if (!messageId) return;

    try {
      await markMessageAsRead(messageId);
      await fetchMessages();
    } catch (error) {
      console.error("Failed to mark message as read:", error);
      setStatus(
        error?.response?.data?.detail ||
          error?.response?.data?.error ||
          error.message ||
          "Failed to mark message as read."
      );
    }
  };

  return (

    <PageWrapper>
    <div className="manualsContainer chatbox">
      <h4 className="testReport">Report your issue</h4>

      <label>Write the issue for manager and get answer ASAP</label>

      {currentUser && (
        <p className="chat-role">
          Current role: <strong>{currentUser.role}</strong>
        </p>
      )}


      <div className="chat-tabs">
        <button
          type="button"
          className={`chat-tab-btn ${activeTab === "submit" ? "active" : ""}`}
          onClick={() => setActiveTab("submit")}
        >
          Submit

        </button>


        <button
          type="button"
          className={`chat-tab-btn ${activeTab === "messages" ? "active" : ""}`}
          onClick={() => setActiveTab("messages")}
        >
          Messages
        </button>
      </div>

      {status && <p className="chat-status">{status}</p>}

      {activeTab === "submit" && (
        <div className="chat-tab-content" ref={formRef}>
          <form onSubmit={handleSubmit}>
            {replyTo && (
              <div className="chat-reply-banner">
                <div>
                  Replying to message <strong>#{replyTo.id}</strong>
                  {replyTo.subject ? <> — {replyTo.subject}</> : null}
                </div>
                <button
                  type="button"
                  className="chat-cancel-reply-btn"
                  onClick={clearReply}
                >
                  Cancel reply
                </button>
              </div>
            )}

            <input
              type="text"
              placeholder="Subject (optional)"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="chat-subject-input"
            />

            <textarea
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="please write the problem"
              required
            />

            {isAdmin && (
              <div className="chat-recipient-box">
                <label className="chat-recipient-label">
                  Recipient IDs (comma-separated)
                </label>
                <input
                  type="text"
                  value={recipientIds}
                  onChange={(e) => setRecipientIds(e.target.value)}
                  placeholder="e.g. 12, 18, 24"
                  className="chat-recipient-input"
                />
                <small className="chat-recipient-help">
                  Required for admin users.
                </small>
              </div>
            )}

            <button
              type="submit"
              className="submitIssueButton"
              disabled={sending}
            >
              {sending ? "Submitting..." : replyTo ? "Send Reply" : "Submit"}
            </button>
          </form>
        </div>
      )}

      {activeTab === "messages" && (
        <div className="chat-tab-content">
          <div className="chat-toolbar">
            <label className="chat-toolbar-label">Message Box:</label>
            <select value={box} onChange={(e) => setBox(e.target.value)}>
              <option value="inbox">Inbox</option>
              <option value="sent">Sent</option>
              <option value="all">All</option>
            </select>

            <button
              type="button"
              onClick={fetchMessages}
              className="chat-refresh-btn"
              title="Refresh"
            >
              <img src={refreshIcon} style={{ width: "24px" }} alt="refresh" />
            </button>
          </div>

          {loading ? (
            <pre>Loading messages...</pre>
          ) : messages.length === 0 ? (
            <pre>— nothing is there yet —</pre>
          ) : (
            <div className="chat-messages">
              {messages.map((msg) => {
                const isRead = Boolean(msg.is_read || msg.read_at);

                const senderId = msg.sender_id ?? msg.sender?.id;
                const senderName = msg.sender?.name || "Unknown";

                const recipientId = msg.recipient_id ?? msg.recipient?.id;
                const recipientName = msg.recipient?.name || "Unknown";

                return (
                  <div
                    key={msg.id || `${msg.subject}-${msg.created_at}`}
                    onClick={() =>
                      !isRead && box === "inbox" && handleMarkAsRead(msg.id)
                    }
                    className={`chat-message-card ${
                      !isRead && box === "inbox" ? "unread" : ""
                    }`}
                  >
                    <div className="chat-message-header">
                      <strong className="chat-message-title">
                        #{msg.id} — {msg.subject || "No Subject"}
                        {!isRead && box === "inbox" && (
                          <img
                            src={riskicon}
                            alt="unread"
                            className="chat-unread-icon"
                          />
                        )}
                      </strong>

                      <small className="chat-message-date">
                        {msg.created_at
                          ? new Date(msg.created_at).toLocaleString()
                          : ""}
                      </small>
                    </div>

                    <div className="chat-message-actions">
                      <button
                        type="button"
                        className="chat-reply-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleReply(msg);
                        }}
                      >
                        Reply
                      </button>
                    </div>

                    <div className="chat-message-meta">
                      <div>
                        <strong>From:</strong> {senderName} (id: {senderId})
                      </div>
                      <div>
                        <strong>To:</strong> {recipientName} (id: {recipientId})
                      </div>
                    </div>

                    <p className="chat-message-body">
                      {msg.body || msg.content || "No message body"}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
    </PageWrapper>

  );
};

export default IranAirChat;
