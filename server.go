package main

import (
	"net/http"
	"strings"
)

func main() {
	mux := http.NewServeMux()

	// Serve specific routes
	mux.HandleFunc("/", serveIndex)
	mux.HandleFunc("/blog", serveFile("blog.html"))
	mux.HandleFunc("/blog/", serveBlogPost)

	// Serve static files
	fileServer := http.FileServer(http.Dir("."))
	mux.Handle("/index.css", fileServer)
	mux.Handle("/index.js", fileServer)
	mux.Handle("/APL386.ttf", fileServer)

	http.ListenAndServe(":3000", mux)
}

func serveIndex(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/" {
		http.ServeFile(w, r, "index.html")
	} else if strings.HasSuffix(r.URL.Path, ".html") || strings.HasSuffix(r.URL.Path, ".js") || strings.HasSuffix(r.URL.Path, ".css") {
		http.FileServer(http.Dir(".")).ServeHTTP(w, r)
	} else {
		http.NotFound(w, r)
	}
}

func serveFile(filename string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, filename)
	}
}

func serveBlogPost(w http.ResponseWriter, r *http.Request) {
	path := strings.TrimPrefix(r.URL.Path, "/blog/")
	http.ServeFile(w, r, "blog/"+path+".html")
}
