import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup} from "@angular/forms";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {map, tap} from "rxjs";
import {animate, style, transition, trigger} from "@angular/animations";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  animations: [
    trigger('fade', [
      transition(':enter', [
        style({opacity: 0}), animate('0.25s', style({opacity: 1}))]
      ),
      transition(':leave',
        [style({opacity: 1}), animate('0.25s', style({opacity: 0}))]
      )
    ])
  ]
})
export class AppComponent implements OnInit {
  title = 'IR Project';

  datasets: { name: string, id: number }[] = [
    {name: 'qura', id: 0},
    {name: 'antique', id: 1}
  ];

  suggestions: { query_id: string, query_text: string }[] = []
  searchResult: { doc_id: string, doc_text: string }[] = [];
  pages: number[] = [];
  pageSizes: number[] = [20, 50, 100, 500, 1e3, 1e6];
  loading: boolean = false;
  disableSuggestion: boolean = false;
  totalCount: number = 0;

  searchFormGroup: FormGroup = new FormGroup({
    datasetId: new FormControl(0),
    page: new FormControl(0),
    pageSize: new FormControl(10),
    query: new FormControl('')
  });

  Array = Array;

  constructor(private http: HttpClient) {
  }

  ngOnInit(): void {
    this.searchFormGroup.controls['datasetId'].valueChanges.subscribe((datasetId) => {
      this.searchFormGroup.controls['page'].setValue(0)
      this.searchFormGroup.controls['pageSize'].setValue(10)
      this.totalCount = 0
      this.pages = []
      this.searchResult = []
      const params = this.searchFormGroup.value as { datasetId: number, query: string };
      this.getSuggestions({
        datasetId,
        query: this.searchFormGroup.controls['query'].value
      })
    })

    this.searchFormGroup.controls['query'].valueChanges.subscribe((query) => {
      if (this.disableSuggestion) return;
      this.getSuggestions({
        datasetId: this.searchFormGroup.controls['datasetId'].value,
        query
      })
    })
  }

  search(params: { datasetId: number, query: string, page: number, pageSize: number }) {
    this.loading = true;
    const payload = {
      page: +params.page || 0,
      pageSize: +params.pageSize || 10,
      query: params.query
    };
    this.searchResult = [];
    this.http.post(`http://127.0.0.1:${params.datasetId === 0 ? 5000 : 4000}/search`, payload).pipe(
      map(res => res as { result: { doc_id: string, doc_text: string }[], total_count: number }),
      tap(() => {
        }, (err: HttpErrorResponse) => {
          this.totalCount = 0;
          this.loading = false;
          this.pages = [];
          this.disableSuggestion = false;
          this.searchFormGroup.setValue({
            ...this.searchFormGroup.value,
            page: 0
          });
          alert("Error: " + err.message);
        }
      )
    ).subscribe((res: { result: { doc_id: string, doc_text: string }[], total_count: number }) => {
      this.disableSuggestion = false;
      this.searchResult = res.result;
      this.totalCount = res.total_count;
      this.pages = [];
      for (let i = payload.pageSize; i < res.total_count; i += payload.pageSize) {
        this.pages.push(i / payload.pageSize);
      }
      this.loading = false;
    })
  }

  suggestionClick(suggestion: { query_id: string; query_text: string }) {
    this.disableSuggestion = true;
    this.suggestions = []
    this.searchFormGroup.setValue({
      ...this.searchFormGroup.value,
      query: suggestion.query_text
    })
    this.search(this.searchFormGroup.value)
  }

  getSuggestions(params: { datasetId: number, query: string }) {
    this.http.post(`http://127.0.0.1:${params.datasetId === 0 ? 5000 : 4000}/get_suggestions`, {
      query: params.query
    }).pipe(
      map(res => res as { result: { query_id: string, query_text: string }[] }),
      tap(() => {
        }, (err: HttpErrorResponse) => {
          this.suggestions = []
        }
      )
    ).subscribe(res => {
      this.suggestions = res.result
    })
  }
}
