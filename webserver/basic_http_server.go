package main

import (
	"fmt"
	"net/http"
)

func helloWorldHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hej verden!")
}

func main() {
	http.HandleFunc("/", helloWorldHandler)
	fmt.Println("Server starting on port 8080...")
	http.ListenAndServe(":8080", nil)
}
