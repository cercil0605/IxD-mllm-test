package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/joho/godotenv"
	"google.golang.org/genai"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, err := fmt.Fprintf(w, "OK")
		if err != nil {
			return
		}
		fmt.Println("health check success")
	})
	// gemini test
	http.HandleFunc("/", handleAnalyzeByGemini)

	log.Println("Listening on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))

}
func handleAnalyzeByGemini(w http.ResponseWriter, r *http.Request) {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		APIKey:  os.Getenv("API_KEY"),
		Backend: genai.BackendGeminiAPI,
	})
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}

	uploadedFile, err := client.Files.UploadFromPath(ctx, "./image/img2.png", nil)
	if err != nil {
		log.Fatalf("Failed to upload image: %v", err)
	}
	bytes, err := ioutil.ReadFile("./prompt/get_score_and_solve.txt")
	if err != nil {
		log.Fatalf("Failed to read file: %v", err)
	}

	parts := []*genai.Part{
		genai.NewPartFromText(string(bytes)),
		genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
	}

	contents := []*genai.Content{
		genai.NewContentFromParts(parts, genai.RoleUser),
	}

	result, err := client.Models.GenerateContent(
		ctx,
		"gemini-2.5-flash",
		contents,
		nil,
	)
	if err != nil {
		log.Fatalf("Failed to generate content: %v", err)
	}
	if result == nil {
		log.Fatal("GenerateContent returned nil result")
	}
	// result.Text() の中身をクリーニングする
	text := result.Text()

	// ```json と ``` を削除
	text = strings.TrimPrefix(text, "```json\n")
	text = strings.TrimSuffix(text, "\n```")

	// パースしてmapに変換（またはstruct）
	var parsed map[string]interface{}
	if err := json.Unmarshal([]byte(text), &parsed); err != nil {
		http.Error(w, "Failed to parse JSON", http.StatusInternalServerError)
		return
	}

	// JSONとしてクライアントに返す
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(parsed)	

	
}
