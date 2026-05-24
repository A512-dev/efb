const IranAirChat=()=>{
return(
    <>
    <div class="manualsContainer">
  

      <h4 class="testReport">Report your issue</h4>
      <label>write the issue for manager and get answer ASAP</label>
      <form>
        <textarea
          
          
          placeholder="please write the problem"
          required
        ></textarea>
        <button
          
          class="submitIssueButton"
          onClick={()=>{alert('your message submitted successfully , wait for the response.')}}
        >
          submit
        </button>
      </form>

      <h2 class="mt-3 mb-1">output :</h2>
      <pre>— nothing is there yet —</pre>
    </div>
    </>
)

}


export default IranAirChat