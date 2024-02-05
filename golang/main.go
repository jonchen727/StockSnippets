package main

import (
	"encoding/json"
	"fmt"
	finance "github.com/piquette/finance-go"
	"github.com/piquette/finance-go/equity"
	"io/ioutil"
)

func main() {
	equities := []string{"AAPL", "GOOGL"} // List of equity symbols
	var data []*finance.Equity             // Slice to store pointers to Equity objects

	for _, symbol := range equities {
		q, err := equity.Get(symbol) // Fetch the equity data
		if err != nil {
			fmt.Println("Error fetching data for:", symbol, err)
			continue // Continue with the next symbol in case of an error
		}
		data = append(data, q) // Append the fetched equity data to the slice
	}

	b, err := json.Marshal(data) // Marshal the data slice to JSON
	if err != nil {
		fmt.Println("Error marshaling data:", err)
		return
	}

	err = ioutil.WriteFile("output.json", b, 0644) // Write the JSON data to a file
	if err != nil {
		fmt.Println("Error writing to file:", err)
		return
	}

	fmt.Println(string(b)) // Optionally print the JSON data
}
