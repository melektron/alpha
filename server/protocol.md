# Basic message

```json
{
  "type": "login|question|answer|request|error|stats",
  (question) "question_type": <0-1>,
  (error) "error_type": <0-2>,
  (request) "request_type": <0-1>,
  (login) "username": "",
  (answer) "answer": ""
}
```

## login message
client:
```json
{
  "type": "login",
  "username": "username"
}
```

server answer:
```json
{
  "type": "confirm"
}
```

or any type of error

## Error types
all errors can have a "cause", but it isn't required for all

### 0 - InvalidLogin
Can occur if the user is already signed in or the questioning has already started.
```json
{
  "type": "error",
  "error_type": 0,
  "cause": "sign in over"
}
```

### 1 - NotLoggedInYet
```json
{
  "type": "error",
  "error_type": 1
}
```

### 2 - InvalidRequest
```json
{
  "type": "error",
  "error_type": 2
}
```

### 3 - InvalidMessage
```json
{
  "type": "error",
  "error_type": 3
}
```

### 4 - QuestionTimeout
```json
{
  "type": "error",
  "error_type": 4
}
```



## Question Types
### 0 - Text Question
server:
```json
{
  "id": int,
  "type": "question",
  "question_type": 0,
  "question": "Question with any text as answer"
}
```

<br>

client reply:
```json
{
  "type": "answer",
  "answer_to": <id of question message>,
  "answer": "whatever the answer may be"
}
```


### 1 - Yes / No Question
server:
```json
{
  "id": int,
  "type": "question",
  "question_type": 1,
  "question": "Question with yes / no as answer"
}
```

client reply:
```json
{
  "type": "answer",
  "answer_to": <id of question message>,
  "answer": bool
}
```

### 2 - Multiple Choice
server:
```json
{
  "id": int,
  "type": "question",
  "question_type": 2,
  "question": "Question",
  "choices": ["choice 1", "choice 2", ...]
}
```

client reply:
```json
{
  "type": "answer",
  "answer_to": <id of question message>,
  "answer": int  // choice index
}
```

## stats
```json
{
  "type": "stats",
  "ranking": [
    [score, "client"]
  ]
}
```