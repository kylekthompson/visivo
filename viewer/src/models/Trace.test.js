import { cleanedPlotData, cleanedTableData, replaceColumnRefWithData } from './Trace';

const exampleData = {
  "traceName": {
    "cohortName": {
      "columns.x_data": [
        1,
        2,
        3,
        4,
        5,
        6
      ],
      "columns.y_data": [
        4,
        -1,
        6,
        -3,
        12,
        -8
      ],
      "props.text": [
        "4",
        "-1",
        "6",
        "-3",
        "12",
        "-8"
      ]
    }
  }
}

test('merge the column data into the referenced property', async () => {
  const traceData = { columns: { x: [0, 1, 2] } }
  const traceObj = { x: "column(x)" }

  replaceColumnRefWithData(traceObj, traceData)

  expect(traceObj.x).toEqual([0, 1, 2])
})

test('merge the column data into the referenced property within an array of arrays', async () => {
  const traceData = { columns: { x: [0, 1, 2], y: [2, 5, 9], z: [1, 2, 3, 4, 5] } }
  const traceObj = { 
    x: ["column(x)", "column(y)"], 
    y: null, 
    z: "column(z)[1]", 
    a: "column(z)[:-2]",
    b: "column(z)[1:-1]",
    c: "column(z)[2:]",
    d: "column(z)[-3]",
    e: ["column(z)[1:3]", "column(z)[2:4]"],
    f: "column(z)[-1]"
  }

  replaceColumnRefWithData(traceObj, traceData)

  expect(traceObj.x).toEqual([[0, 1, 2], [2, 5, 9]])
  expect(traceObj.z).toEqual(2)
  expect(traceObj.a).toEqual([1,2,3])
  expect(traceObj.b).toEqual([2,3,4])
  expect(traceObj.d).toEqual(3)
  expect(traceObj.e).toEqual([[2,3], [3,4]])
  expect(traceObj.f).toEqual(5)
})


test('cleaned plot data', async () => {
  const traceObj = { name: "traceName", columns: { x: "x_data" }, props: { x: "column(x_data)" } }

  const plotData = cleanedPlotData(exampleData, traceObj)

  expect(plotData).toEqual([{
    "name": "cohortName",
    "x": exampleData["traceName"]["cohortName"]["columns.x_data"],
    "text": exampleData["traceName"]["cohortName"]["props.text"]
  }])
})

test('cleaned indicator data', async () => {
  const traceObj = { name: "traceName", columns: { x: "x_data" }, props: { x: "column(x_data)[0]" } }

  const plotData = cleanedPlotData(exampleData, traceObj)

  expect(plotData).toEqual([{
    "name": "cohortName",
    "x": exampleData["traceName"]["cohortName"]["columns.x_data"][0],
    "text": exampleData["traceName"]["cohortName"]["props.text"]
  }])
})

test('cleaned table data', async () => {
  const tableObj = {
    name: "awesome-table",
    props: { enableColumnDragging: true },
    trace: { name: "traceName", columns: { x: "x_data", y: "y_data" }, props: { x: "column(x_data)" } },
    columns: [
      { header: "X Data", column: "x_data" },
      { header: "Y Data", column: "y_data" }]
  }

  const tableData = cleanedTableData(exampleData, tableObj)

  expect(tableData).toEqual([
    { "x_data": 1, "y_data": 4 },
    { "x_data": 2, "y_data": -1 },
    { "x_data": 3, "y_data": 6 },
    { "x_data": 4, "y_data": -3 },
    { "x_data": 5, "y_data": 12 },
    { "x_data": 6, "y_data": -8 }
  ])
})