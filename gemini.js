const { GoogleGenerativeAI } = require("@google/generative-ai");
const readline = require("readline");

// Configuração
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function chat() {
    console.log("\n--- Gemini CLI Iniciada (digite 'sair' para encerrar) ---");
    const ask = () => {
        rl.question("Você: ", async (input) => {
            if (input.toLowerCase() === "sair") return rl.close();
            
            try {
                const result = await model.generateContent(input);
                console.log("\nGemini:", result.response.text(), "\n");
            } catch (err) {
                console.error("Erro:", err.message);
            }
            ask();
        });
    };
    ask();
}

chat();